import { useState } from 'react'
import type { ScrapeStatus } from '../types/api'

export function ProgressPanel({ status }: { status: ScrapeStatus | null }) {
  const [showDone, setShowDone] = useState(false)

  if (!status) return null

  const { keywords, total_keywords, completed_keywords, email_found } = status
  if (keywords.length === 0 && completed_keywords === 0) return null

  const running = keywords.filter((k) => k.status === 'running')
  const done = keywords.filter((k) => k.status === 'done')
  const failed = keywords.filter((k) => k.status === 'failed')
  const queued = keywords.filter((k) => k.status === 'queued')

  const totalBusinessSucceeded = done.reduce((s, k) => s + k.succeeded, 0)
  const totalBusinessSkipped = done.reduce((s, k) => s + k.skipped, 0)

  return (
    <div className="progress-panel">
      {/* 总览条 */}
      <div className="progress-summary">
        <span className="summary-item">
          关键词 {completed_keywords}/{total_keywords}
        </span>
        <span className="summary-sep">·</span>
        <span className="summary-item">
          <span className="s-ok">✓</span>{totalBusinessSucceeded} <span className="s-fail">✗</span>{totalBusinessSkipped}
        </span>
        <span className="summary-sep">·</span>
        <span className="summary-item">邮箱 {email_found}</span>
        {queued.length > 0 && (
          <>
            <span className="summary-sep">·</span>
            <span className="summary-item muted">排队 {queued.length}</span>
          </>
        )}
      </div>

      {/* 进行中网格 */}
      {running.length > 0 && (
        <div className="progress-section">
          <div className="progress-section-title">进行中 ({running.length})</div>
          <div className="progress-grid">
            {running.map((kw) => (
              <div key={kw.keyword} className="progress-card">
                <div className="progress-card-title">{kw.keyword}</div>
                {kw.found > 0 ? (
                  <>
                    <div className="progress-bar-wrap">
                      <div
                        className="progress-bar-fill"
                        style={{ width: `${kw.found > 0 ? (kw.processed / kw.found) * 100 : 0}%` }}
                      />
                    </div>
                    <div className="progress-card-stats">
                      {kw.processed}/{kw.found}
                      <span className="s-ok">✓{kw.succeeded}</span>
                      <span className="s-fail">✗{kw.skipped}</span>
                    </div>
                  </>
                ) : (
                  <div className="progress-card-stats muted">搜索中...</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 已完成折叠区 */}
      {done.length > 0 && (
        <div className="progress-section">
          <div
            className="progress-section-title toggle"
            onClick={() => setShowDone(!showDone)}
          >
            已完成 ({done.length}) <span className="toggle-arrow">{showDone ? '▾' : '▸'}</span>
          </div>
          {showDone && (
            <div className="progress-done-tags">
              {done.map((kw) => (
                <span key={kw.keyword} className="done-tag">
                  {kw.keyword} <span className="s-ok">✓{kw.succeeded}</span>
                  {kw.skipped > 0 && <span className="s-fail">✗{kw.skipped}</span>}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 失败折叠区 */}
      {failed.length > 0 && (
        <div className="progress-section">
          <div
            className="progress-section-title toggle error"
            onClick={() => setShowDone(!showDone)}
          >
            失败 ({failed.length})
          </div>
          {showDone && (
            <div className="progress-done-tags">
              {failed.map((kw) => (
                <span key={kw.keyword} className="done-tag fail">
                  {kw.keyword}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}