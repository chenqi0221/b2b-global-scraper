use std::net::TcpStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::Duration;

use tauri::Manager;

/// 子进程中的 Python 后端（开发期 Python；生产期 PyInstaller sidecar exe）。release 模式优先尝试 bundle 里的 backend.exe。
pub struct BackendChild(pub Mutex<Option<Child>>);

fn fallback_repo_root_from_manifest() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("tauri-app")
        .parent()
        .expect("repo root")
        .to_path_buf()
}

fn looks_like_repo_root(p: &Path) -> bool {
    p.join("backend").join("main.py").is_file()
}

/// release 模式下，backend.exe 会作为 externalBin 打包到 app.exe 同目录。
/// Tauri v2 可能保留或不保留目标三元组后缀，两个名字都尝试。
fn bundled_backend_exe() -> Option<PathBuf> {
    let Ok(exe) = std::env::current_exe() else {
        return None;
    };
    let dir = exe.parent().unwrap_or(Path::new("."));
    for name in &[
        "backend.exe",
        "backend-x86_64-pc-windows-msvc.exe",
    ] {
        let bundled = dir.join(name);
        if bundled.is_file() {
            log::info!("found bundled backend: {}", bundled.display());
            return Some(bundled);
        }
    }
    None
}

/// 从 exe 路径向上查找，直到找到包含 backend/main.py 的目录。
fn repo_root_from_exe(exe: &Path) -> Option<PathBuf> {
    let mut dir = exe.parent()?;
    for _ in 0..6 {
        if looks_like_repo_root(dir) {
            return Some(dir.to_path_buf());
        }
        dir = dir.parent()?;
    }
    None
}

/// 仓库根：优先 `B2B_REPO_ROOT`；否则从 `current_exe()` 推断；最后回退编译期路径。
fn repo_root() -> PathBuf {
    if let Ok(raw) = std::env::var("B2B_REPO_ROOT") {
        let p = PathBuf::from(raw.trim());
        if looks_like_repo_root(&p) {
            return p;
        }
        log::warn!("B2B_REPO_ROOT is set but backend/main.py not found there; ignoring");
    }

    let Ok(exe) = std::env::current_exe() else {
        return fallback_repo_root_from_manifest();
    };

    if let Some(root) = repo_root_from_exe(&exe) {
        return root;
    }

    log::warn!("repo_root: using compile-time manifest parent (wrong if app was moved)");
    fallback_repo_root_from_manifest()
}

#[tauri::command]
fn reveal_path(path: String) -> Result<(), String> {
    let p = PathBuf::from(&path);
    if !p.exists() {
        return Err("路径不存在".into());
    }
    #[cfg(target_os = "windows")]
    {
        if p.is_file() {
            let arg = format!("/select, {}", p.display());
            Command::new("explorer")
                .arg(arg)
                .spawn()
                .map_err(|e| e.to_string())?;
        } else {
            Command::new("explorer")
                .arg(&p)
                .spawn()
                .map_err(|e| e.to_string())?;
        }
    }
    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(&p)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    #[cfg(all(not(target_os = "windows"), not(target_os = "macos")))]
    {
        Command::new("xdg-open")
            .arg(&p)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    Ok(())
}

fn wait_for_backend(addr: &str, max_secs: u64) -> bool {
    for i in 0..max_secs {
        if TcpStream::connect(addr).is_ok() {
            log::info!("python backend ready at {addr} after {i}s");
            return true;
        }
        thread::sleep(Duration::from_secs(1));
    }
    false
}

#[cfg(windows)]
fn kill_port_8756() {
    use std::process::Command as StdCommand;
    let out = StdCommand::new("cmd")
        .args(["/C", "for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :8756') do taskkill /F /PID %a 2>nul"])
        .output();
    match out {
        Ok(o) if !o.status.success() => {
            log::info!("port 8756 cleanup: {}", String::from_utf8_lossy(&o.stdout).trim());
        }
        _ => {}
    }
}

fn spawn_bundled_backend() -> Option<Child> {
    let exe = match bundled_backend_exe() {
        Some(p) => p,
        None => {
            log::warn!("bundled backend exe not found in app dir");
            return None;
        }
    };
    let dir = exe.parent();
    log::info!("bundled backend exe path: {}", exe.display());

    for attempt in 0..2 {
        if attempt > 0 {
            log::warn!("bundled backend attempt {} retrying after 3s...", attempt + 1);
            thread::sleep(Duration::from_secs(3));
        }

        #[cfg(windows)]
        kill_port_8756();

        let mut cmd = Command::new(&exe);
        if let Some(dir) = dir {
            cmd.current_dir(dir);
            cmd.env("B2B_REPO_ROOT", dir);
        }
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x08000000;
            cmd.creation_flags(CREATE_NO_WINDOW);
        }
        match cmd.spawn() {
            Ok(mut ch) => {
                log::info!("bundled backend.exe spawned (attempt {}), waiting for 127.0.0.1:8756 ...", attempt + 1);
                if wait_for_backend("127.0.0.1:8756", 45) {
                    return Some(ch);
                }
                log::warn!("bundled backend port 8756 not ready in 45s");
                let _ = ch.kill();
                #[cfg(windows)]
                kill_port_8756();
            }
            Err(e) => log::warn!("bundled backend spawn failed: {e}"),
        }
    }
    log::error!("bundled backend failed after 2 attempts");
    None
}

fn spawn_python_backend(root: &Path) -> Option<Child> {
    let uvicorn_args = [
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8756",
    ];

    #[cfg(windows)]
    let attempts: &[(&str, &[&str])] = &[
        ("python", &uvicorn_args),
        ("py", &["-3", "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8756"]),
    ];

    #[cfg(not(windows))]
    let attempts: &[(&str, &[&str])] = &[
        ("python3", &uvicorn_args),
        ("python", &uvicorn_args),
    ];

    for (prog, args) in attempts {
        let mut cmd = Command::new(prog);
        cmd.args(*args).current_dir(root);
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x08000000;
            cmd.creation_flags(CREATE_NO_WINDOW);
        }
        match cmd.spawn() {
            Ok(mut ch) => {
                log::info!("python backend spawned via {prog}, waiting for 127.0.0.1:8756 ...");
                if wait_for_backend("127.0.0.1:8756", 45) {
                    return Some(ch);
                }
                log::warn!("backend spawned via {prog} but port 8756 not ready in 45s; killing and trying next");
                let _ = ch.kill();
            }
            Err(e) => log::warn!("backend spawn try {prog} failed: {e}"),
        }
    }
    log::warn!("python backend could not be started (install Python / py launcher, PATH when double-clicking exe may differ from terminal)");
    None
}

#[tauri::command]
fn check_backend_health() -> String {
    if TcpStream::connect("127.0.0.1:8756").is_ok() {
        "alive".into()
    } else {
        "dead".into()
    }
}

#[tauri::command]
fn restart_backend(app: tauri::AppHandle) -> Result<String, String> {
    let st = app.state::<BackendChild>();
    let mut slot = st.0.lock().map_err(|e| e.to_string())?;

    if let Some(mut c) = slot.take() {
        let _ = c.kill();
        log::info!("python backend killed for restart");
    }

    #[cfg(windows)]
    kill_port_8756();

    std::thread::sleep(std::time::Duration::from_secs(2));

    let new_child = spawn_bundled_backend().or_else(|| {
        let root = repo_root();
        spawn_python_backend(&root)
    });

    match new_child {
        Some(ch) => {
            log::info!("python backend restarted successfully");
            *slot = Some(ch);
            Ok("后端已重启".into())
        }
        None => {
            log::error!("python backend restart failed");
            Err("后端重启失败".into())
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, argv, _cwd| {
            log::info!("single-instance argv={argv:?}");
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.set_focus();
            }
        }))
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_window_state::Builder::default().build())
        .invoke_handler(tauri::generate_handler![
            reveal_path,
            check_backend_health,
            restart_backend
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            let py_child = spawn_bundled_backend().or_else(|| {
                let root = repo_root();
                spawn_python_backend(&root)
            });

            if py_child.is_none() {
                log::error!("python backend failed to start; app will run but API calls will fail");
            }
            app.manage(BackendChild(Mutex::new(py_child)));

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if matches!(event, tauri::RunEvent::Exit) {
                if let Some(st) = app_handle.try_state::<BackendChild>() {
                    if let Ok(mut g) = st.0.lock() {
                        if let Some(mut c) = g.take() {
                            let _ = c.kill();
                            log::info!("python backend stopped");
                        }
                    }
                }
            }
        });
}
