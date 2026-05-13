use std::net::TcpStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::Duration;

use tauri::Manager;

/// 子进程中的 Python FastAPI（开发期由 Tauri 拉起；生产换 PyInstaller sidecar）。
pub struct BackendChild(pub Mutex<Option<Child>>);

/// WhatsApp Node（`third_party/whatsapp-service/web.js`），可由用户或 `B2B_SPAWN_WHATSAPP=1` 拉起。
pub struct WhatsappChild(pub Mutex<Option<Child>>);

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

    if let Some(bin_dir) = exe.parent() {
        let name = bin_dir.file_name().and_then(|s| s.to_str()).unwrap_or("");
        if name.eq_ignore_ascii_case("release") || name.eq_ignore_ascii_case("debug") {
            let mut dir = bin_dir.to_path_buf();
            for _ in 0..4 {
                if let Some(p) = dir.parent() {
                    dir = p.to_path_buf();
                } else {
                    return fallback_repo_root_from_manifest();
                }
            }
            if looks_like_repo_root(&dir) {
                return dir;
            }
        }
    }

    if let Some(parent) = exe.parent() {
        if looks_like_repo_root(parent) {
            return parent.to_path_buf();
        }
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
            let arg = format!("/select,{}", p.display());
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
        ("py", &["-3", "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8756"]),
        ("python", &uvicorn_args),
    ];

    #[cfg(not(windows))]
    let attempts: &[(&str, &[&str])] = &[
        ("python3", &uvicorn_args),
        ("python", &uvicorn_args),
    ];

    for (prog, args) in attempts {
        let mut cmd = Command::new(prog);
        cmd.args(*args).current_dir(root).stdout(Stdio::null()).stderr(Stdio::null());
        match cmd.spawn() {
            Ok(mut ch) => {
                log::info!("python backend spawned via {prog}, waiting for 127.0.0.1:8756 ...");
                if wait_for_backend("127.0.0.1:8756", 15) {
                    return Some(ch);
                }
                log::warn!("backend spawned via {prog} but port 8756 not ready in 15s; killing and trying next");
                let _ = ch.kill();
            }
            Err(e) => log::warn!("backend spawn try {prog} failed: {e}"),
        }
    }
    log::warn!("python backend could not be started (install Python / py launcher, PATH when double-clicking exe may differ from terminal)");
    None
}

fn try_spawn_whatsapp_child(root: &Path) -> Result<Child, String> {
    let wa_dir = root.join("third_party").join("whatsapp-service");
    let script = wa_dir.join("web.js");
    let nm = wa_dir.join("node_modules");
    if !script.is_file() {
        return Err("缺少 third_party/whatsapp-service/web.js".into());
    }
    if !nm.is_dir() {
        return Err("请在 third_party/whatsapp-service 目录执行 npm install".into());
    }
    let mut cmd = Command::new("node");
    cmd.current_dir(&wa_dir)
        .arg("web.js")
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    cmd.spawn().map_err(|e| format!("启动 node 失败: {e}"))
}

/// 设置 `B2B_SPAWN_WHATSAPP=1` 且已 `npm install` 时，尝试 `node web.js`。
fn maybe_spawn_whatsapp(root: &Path) -> Option<Child> {
    let Ok(flag) = std::env::var("B2B_SPAWN_WHATSAPP") else {
        return None;
    };
    if flag != "1" {
        return None;
    }
    match try_spawn_whatsapp_child(root) {
        Ok(ch) => {
            log::info!("whatsapp node auto-spawn (B2B_SPAWN_WHATSAPP=1)");
            Some(ch)
        }
        Err(e) => {
            log::warn!("whatsapp auto-spawn skipped: {e}");
            None
        }
    }
}

#[tauri::command]
fn whatsapp_service_start(app: tauri::AppHandle) -> Result<String, String> {
    let root = repo_root();
    let st = app.state::<WhatsappChild>();
    let mut slot = st.0.lock().map_err(|e| e.to_string())?;
    if slot.is_some() {
        return Ok("WhatsApp 服务已在运行".into());
    }
    let ch = try_spawn_whatsapp_child(&root)?;
    log::info!("whatsapp node started by user command");
    *slot = Some(ch);
    Ok("已启动 WhatsApp Node（默认端口见服务配置）".into())
}

#[tauri::command]
fn whatsapp_service_stop(app: tauri::AppHandle) -> Result<(), String> {
    let st = app.state::<WhatsappChild>();
    let mut slot = st.0.lock().map_err(|e| e.to_string())?;
    if let Some(mut c) = slot.take() {
        let _ = c.kill();
        log::info!("whatsapp node stopped by user command");
    }
    Ok(())
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
            whatsapp_service_start,
            whatsapp_service_stop
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            let root = repo_root();
            let py_child = spawn_python_backend(&root);
            if py_child.is_none() {
                log::error!("python backend failed to start; app will run but API calls will fail");
            }
            app.manage(BackendChild(Mutex::new(py_child)));

            let wa_child = maybe_spawn_whatsapp(&root);
            app.manage(WhatsappChild(Mutex::new(wa_child)));

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if matches!(event, tauri::RunEvent::Exit) {
                if let Some(st) = app_handle.try_state::<WhatsappChild>() {
                    if let Ok(mut g) = st.0.lock() {
                        if let Some(mut c) = g.take() {
                            let _ = c.kill();
                            log::info!("whatsapp node stopped");
                        }
                    }
                }
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
