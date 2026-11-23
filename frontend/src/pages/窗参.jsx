import React, { useEffect, useState } from "react";
import { 取 } from "../api.js";

export default function 窗参页() {
  const [规, 设规] = useState(null);
  const [桩, 设桩] = useState([]);
  useEffect(() => {
    取("/站规").then(设规);
    取("/空桩").then(设桩);
  }, []);
  if (!规) return <p className="讯">加载中…</p>;
  const 主参 = ["窗长秒", "允许迟到秒", "关窗条件", "旁路条件", "水位推进策略"];
  return (
    <div>
      <h1 className="题">窗参</h1>
      <p className="述">窗长、允许迟到、关窗/旁路条件。邻题空桩挂在这里，不参与主链。</p>
      <div className="段">
        <div className="段题">主链参数</div>
        <table>
          <thead><tr><th>键</th><th>值</th></tr></thead>
          <tbody>
            {主参.filter((k) => 规[k] != null).map((k) => (
              <tr key={k}><td>{k}</td><td className="码">{规[k]}</td></tr>
            ))}
            {Object.entries(规)
              .filter(([k]) => !主参.includes(k))
              .map(([k, v]) => (
                <tr key={k}><td>{k}</td><td className="码">{v}</td></tr>
              ))}
          </tbody>
        </table>
      </div>
      <div className="段">
        <div className="段题">邻题空桩</div>
        <table>
          <thead><tr><th>名</th><th>状态</th></tr></thead>
          <tbody>{桩.map((p) => <tr key={p.名}><td>{p.名}</td><td>{p.状态}</td></tr>)}</tbody>
        </table>
      </div>
    </div>
  );
}
