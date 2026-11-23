import React, { useEffect, useState } from "react";
import { 取 } from "../api.js";

export default function 旁路匣页() {
  const [行, 设] = useState([]);
  const 刷 = () => 取("/旁路匣").then(设);
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">⑤ 旁路匣</h1>
      <p className="述">
        水位已越过「该事件所属窗的窗止 + 允许迟到」时，事件不得再改已关窗，落入旁路匣。侧输出，不是隔离金库。
      </p>
      <div className="行"><button className="次" onClick={刷}>刷新旁路</button></div>
      {!行.length ? (
        <div className="空态">暂无旁路。推完迟到修正后再推「超迟到旁路样例」。</div>
      ) : (
        <table>
          <thead>
            <tr><th>编号</th><th>原因</th><th>载荷</th><th>时刻</th></tr>
          </thead>
          <tbody>
            {行.map((r) => (
              <tr key={r.编号}>
                <td>{r.编号}</td><td>{r.原因}</td>
                <td className="码">{r.载荷}</td><td className="码">{r.时刻}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
