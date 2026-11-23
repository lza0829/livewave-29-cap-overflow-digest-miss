import React, { useEffect, useState } from "react";
import { 取, 递 } from "../api.js";

export default function 窗互证页() {
  const [列, 设列] = useState([]);
  const [果, 设果] = useState(null);
  const 刷 = () => 取("/贯验").then(设列);
  useEffect(() => { 刷(); }, []);
  const 跑 = async () => {
    设果(await 递("/贯验"));
    刷();
  };
  return (
    <div>
      <h1 className="题">窗互证</h1>
      <p className="述">
        核对：已关闭窗的点赞/送礼/笔数 = 落入该窗的事件合计；若有撤回，末次撤回的新值须与窗表一致。不是枢纽-链接-卫星贯验。
      </p>
      <div className="行">
        <button className="水" onClick={跑}>跑窗互证</button>
        <button className="次" onClick={刷}>刷新履历</button>
      </div>
      {果 && (
        <div className="证板">
          <div className={`证旗 ${果.是否通过 ? "通" : "败"}`}>
            <div className="标">{果.是否通过 ? "对齐" : "撕裂"}</div>
            <div className="辅">{果.说明}</div>
          </div>
          <div className="格">
            <div className="卡"><b>{果.事件数}</b><span>事件</span></div>
            <div className="卡"><b>{果.已关闭窗数}</b><span>已关窗</span></div>
            <div className="卡"><b>{果.撤回数}</b><span>撤回</span></div>
            <div className="卡"><b>{果.旁路数}</b><span>旁路</span></div>
          </div>
        </div>
      )}
      <div className="段">
        <div className="段题">互证履历</div>
        {!列.length ? (
          <div className="空态">尚无履历</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>编号</th><th>时刻</th><th>结果</th><th>事件</th><th>关窗</th><th>撤回</th><th>旁路</th><th>说明</th>
              </tr>
            </thead>
            <tbody>
              {列.map((r) => (
                <tr key={r.编号}>
                  <td>{r.编号}</td><td className="码">{r.时刻}</td>
                  <td><span className={`徽章 ${r.是否通过 ? "通" : "败"}`}>{r.是否通过 ? "对齐" : "撕裂"}</span></td>
                  <td>{r.事件数}</td><td>{r.已关闭窗数}</td><td>{r.撤回数}</td><td>{r.旁路数}</td>
                  <td>{r.说明}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
