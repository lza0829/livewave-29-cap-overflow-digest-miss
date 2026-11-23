import React, { useEffect, useState } from "react";
import { 取, 递 } from "../api.js";

const 夹具 = ["准时热度样例", "迟到修正样例", "超迟到旁路样例", "超上限旁路样例", "超额迟到并发样例"];

export default function 事件流() {
  const [事, 设事] = useState([]);
  const [报, 设报] = useState(null);
  const [选, 设选] = useState(夹具[0]);
  const 刷 = () => 取("/事件").then(设事);
  useEffect(() => { 刷(); }, []);
  const 推 = async () => {
    const r = await 递(`/装载/夹具?名=${encodeURIComponent(选)}`);
    设报(r);
    刷();
  };
  return (
    <div>
      <h1 className="题">① 事件流</h1>
      <p className="述">
        推入带「事件时 / 处理时」的互动点。每次推送会抬水位、尝试关窗，并可能写出撤回或旁路——不是「入湖落三件套」。
      </p>
      <div className="提示条">建议顺序：准时（关第一窗）→ 迟到修正（出撤回单）→ 超迟到（旁路匣）。</div>
      <div className="行">
        {夹具.map((n) => (
          <button key={n} className={`次 ${选 === n ? "亮片" : ""}`} onClick={() => 设选(n)}>{n}</button>
        ))}
        <button className="水" onClick={推}>推入并抬水位</button>
        <button className="次" onClick={刷}>刷新事件</button>
      </div>
      {报 && (
        <div className="报箱 码">
          {`入窗 ${报.入窗} · 撤回 ${报.撤回} · 旁路 ${报.旁路} · 新关窗 ${报.新关窗}\n`}
          {JSON.stringify(报.明细, null, 2)}
        </div>
      )}
      <div className="段">
        <div className="段题">事件命运</div>
        {!事.length ? (
          <div className="空态">还没有事件。选一份样例推入。</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>事件编号</th><th>房间</th><th>类型</th><th>事件时</th><th>处理时</th>
                <th>点赞</th><th>送礼</th><th>命运</th><th>落入窗</th>
              </tr>
            </thead>
            <tbody>
              {事.map((r) => (
                <tr key={r.事件编号}>
                  <td>{r.事件编号}</td><td>{r.房间键}</td><td>{r.事件类型}</td>
                  <td className="码">{r.事件时}</td><td className="码">{r.处理时}</td>
                  <td>{r.点赞增量}</td><td>{r.送礼额}</td><td>{r.命运}</td>
                  <td className="码">{r.窗键 || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
