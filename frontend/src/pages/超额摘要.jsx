import React, { useEffect, useState } from "react";
import { 取 } from "../api.js";

export default function 超额摘要() {
  const [体, 设体] = useState(null);
  const [err, setErr] = useState("");
  const 刷 = () => {
    取("/核证/超额摘要")
      .then((b) => { 设体(b); setErr(""); })
      .catch((e) => setErr(String(e.message || e)));
  };
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">超额摘要核证</h1>
      <p className="述">
        口径：<b>{体 ? 体.口径 : "…"}</b>。上限处置（整笔旁路）成功必须同票写超额摘要
        （窗键 / 上限 / 实际入窗额 / 截断额或旁路事件号 / 摘要号）；迟到撤回只动摘要入窗额，
        扣减不得超过实际入窗额，被截断/旁路的部分禁止当已入窗回滚。本库不采用「差额工单放行全额」
        （可按面额全额={体 ? String(体.可按面额全额) : "…"}，需差额工单={体 ? String(体.需差额工单) : "…"}）。
      </p>
      {err && <pre className="码">{err}</pre>}
      <div className="行">
        <span className={`徽章 ${体 && 体.valid ? "通" : "败"}`}>
          {body(体)}
        </span>
        <span className="讯" style={{ margin: 0 }}>摘要数 {体 ? 体.摘要数 : "—"}</span>
        <button className="次" onClick={刷}>刷新</button>
      </div>
      {体 && 体.问题 && 体.问题.length > 0 && (
        <div className="报箱 码">{体.问题.join("\n")}</div>
      )}
      {!体 ? (
        <div className="空态">加载中…</div>
      ) : !体.超额摘要.length ? (
        <div className="空态">暂无超额摘要。推「超上限旁路样例」触发上限处置后即可见。</div>
      ) : (
        <div className="段">
          <div className="段题">超额摘要（上限处置留证）</div>
          <table>
            <thead>
              <tr>
                <th>摘要号</th><th>窗键</th><th>上限</th><th>实际入窗额</th>
                <th>截断额</th><th>旁路事件号</th><th>时刻</th><th>核证</th>
              </tr>
            </thead>
            <tbody>
              {体.超额摘要.map((r) => (
                <tr key={r.编号}>
                  <td className="码">{r.摘要号}</td>
                  <td className="码">{r.窗键}</td>
                  <td>{r.上限}</td>
                  <td>{r.实际入窗额}</td>
                  <td>{r.截断额}</td>
                  <td className="码">{r.旁路事件号 || "—"}</td>
                  <td className="码">{r.时刻}</td>
                  <td>
                    <span className={`徽章 ${r.核证 && r.核证.通过 ? "通" : "败"}`}>
                      {r.核证 && r.核证.通过 ? "合法" : "异常"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {体 && 体.协同 && (
        <div className="段">
          <div className="段题">协同</div>
          <table>
            <tbody>
              {Object.entries(体.协同).map(([k, v]) => (
                <tr key={k}><td>{k}</td><td>{String(v)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function body(体) {
  if (!体) return "加载中…";
  return 体.valid ? "摘要合法" : "摘要异常";
}
