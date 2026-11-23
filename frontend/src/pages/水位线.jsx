import React, { useEffect, useState } from "react";
import { 取 } from "../api.js";

export default function 水位线页() {
  const [房, 设] = useState([]);
  const 刷 = () => 取("/直播间").then(设);
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">② 水位线</h1>
      <p className="述">
        每房一条<strong>事件时水位</strong>（已见最大事件时）。规则：水位 ≥ 窗止 → 关窗发射；水位 ≥ 窗止 + 允许迟到 → 该窗拒收迟到（进旁路）。
      </p>
      <div className="行"><button className="次" onClick={刷}>刷新水位</button></div>
      {!房.length ? (
        <div className="空态">无直播间</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>房间</th><th>标题</th><th>主播</th><th>开播事件时</th>
              <th>事件时水位</th><th>允许迟到秒</th><th>水位更新处理时</th>
            </tr>
          </thead>
          <tbody>
            {房.map((r) => {
              const w = r.水位线 || {};
              return (
                <tr key={r.房间键}>
                  <td>{r.房间键}</td><td>{r.标题}</td><td>{r.主播}</td>
                  <td className="码">{r.开播事件时}</td>
                  <td className="码">{w.事件时水位 || "—"}</td>
                  <td>{w.允许迟到秒 ?? "—"}</td>
                  <td className="码">{w.更新处理时 || "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
