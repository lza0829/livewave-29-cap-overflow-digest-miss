import React, { useEffect, useState } from "react";
import { 取 } from "../api.js";

export default function 撤回单页() {
  const [行, 设] = useState([]);
  const 刷 = () => 取("/撤回单").then(设);
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">④ 撤回单</h1>
      <p className="述">
        已关闭窗在「窗止 + 允许迟到」之前又进来事件时：先改窗合计，再记一笔撤回（旧值 → 新值）。这是窗计算的修正链，不是装载回滚。
      </p>
      <div className="行"><button className="次" onClick={刷}>刷新撤回</button></div>
      {!行.length ? (
        <div className="空态">暂无撤回。准时关窗后再推「迟到修正样例」。</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>编号</th><th>窗键</th><th>原因</th><th>点赞旧→新</th><th>送礼旧→新</th><th>触发事件</th><th>处理时</th>
            </tr>
          </thead>
          <tbody>
            {行.map((r) => (
              <tr key={r.编号}>
                <td>{r.编号}</td><td className="码">{r.窗键}</td><td>{r.原因}</td>
                <td>{r.旧点赞} → {r.新点赞}</td><td>{r.旧送礼} → {r.新送礼}</td>
                <td>{r.事件编号}</td><td className="码">{r.处理时}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
