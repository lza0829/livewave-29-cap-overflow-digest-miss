import React, { useEffect, useState } from "react";
import { 取 } from "../api.js";

export default function 上限闸页() {
  const [况, 设况] = useState(null);
  const 刷 = () => 取("/上限闸").then(设况);
  useEffect(() => { 刷(); }, []);
  if (!况) return <p className="讯">加载中…</p>;
  const 证据列 = 况.窗.flatMap((w) => w.证据.map((e) => ({ ...e, 窗键: w.窗键 })));
  return (
    <div>
      <h1 className="题">上限闸</h1>
      <p className="述">
        单窗主指标（{况.主指标}）触站规热度上限 <b>{况.上限}</b> 即整笔旁路留证（{况.策略}）：
        窗合计保持上限下最后合法值，不落撤回单。一笔过大点赞后——窗合计不变且旁路有该事件，
        即本口径签名；若窗合计=上限且无旁路，则是未采用的「截断入窗」口径。
      </p>
      <div className="行">
        <span className={`徽章 ${况.valid ? "通" : "败"}`}>{况.valid ? "闸况合法" : "闸况异常"}</span>
        <span className="讯" style={{ margin: 0 }}>越限窗 {况.越限窗数} / {况.窗数}</span>
        <button className="次" onClick={刷}>刷新闸况</button>
      </div>
      {!况.窗.length ? (
        <div className="空态">暂无热度窗。先去事件流推样例。</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>窗键</th><th>状态</th><th>上限</th><th>窗合计</th><th>余量</th>
              <th>顶格</th><th>证据</th><th>valid</th>
            </tr>
          </thead>
          <tbody>
            {况.窗.map((w) => (
              <tr key={w.窗键}>
                <td className="码">{w.窗键}</td>
                <td>{w.状态}</td>
                <td>{w.上限}</td>
                <td>{w.窗合计}</td>
                <td>{w.余量}</td>
                <td>{w.顶格 ? "顶格" : w.越限 ? "越限!" : "—"}</td>
                <td>{w.证据.length}</td>
                <td><span className={`徽章 ${w.valid ? "通" : "败"}`}>{w.valid ? "合法" : "异常"}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="段">
        <div className="段题">超上限旁路证据</div>
        {!证据列.length ? (
          <div className="空态">暂无超上限旁路。推「超上限旁路样例」可见。</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>事件编号</th><th>窗键本应</th><th>窗合计</th><th>点赞增量</th>
                <th>若入窗合计</th><th>迟到修正</th><th>时刻</th>
              </tr>
            </thead>
            <tbody>
              {证据列.map((e) => (
                <tr key={e.编号}>
                  <td>{e.事件编号}</td>
                  <td className="码">{e.窗键本应}</td>
                  <td>{e.窗合计}</td>
                  <td>{e.点赞增量}</td>
                  <td>{e.若入窗合计}</td>
                  <td>{e.迟到修正 ? "是" : "否"}</td>
                  <td className="码">{e.时刻}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
