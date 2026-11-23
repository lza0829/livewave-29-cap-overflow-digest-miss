import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { 取 } from "../api.js";

export default function 热度台() {
  const [数, 设] = useState(null);
  const 刷 = () => 取("/总览").then(设);
  useEffect(() => { 刷(); }, []);
  if (!数) return <p className="讯">加载中…</p>;
  const 末 = 数.末次贯验;
  return (
    <div>
      <h1 className="题">热度台</h1>
      <p className="述">
        这里不是装载金库台。主路径是：事件按<strong>事件时</strong>推进水位 → 水位越过窗止则<strong>关闭热度窗</strong> →
        允许迟到内修正发<strong>撤回单</strong> → 越过窗止+迟到则进<strong>旁路匣</strong> → 最后做窗合计互证。
      </p>
      <div className="阶条">
        <div className="阶"><div className="序">① 事件流</div><b>{数.互动事件 ?? 0}</b><span>已见事件</span></div>
        <div className="阶"><div className="序">② 水位 / 开窗</div><b>{数.开启窗 ?? 0}</b><span>开启中窗</span></div>
        <div className="阶"><div className="序">③ 已关窗</div><b>{数.已关闭窗 ?? 0}</b><span>已发射</span></div>
        <div className="阶"><div className="序">④ 撤回</div><b>{数.撤回单数 ?? 数.撤回单 ?? 0}</b><span>迟到修正</span></div>
        <div className="阶"><div className="序">⑤ 旁路</div><b>{数.旁路匣 ?? 0}</b><span>超允许迟到</span></div>
      </div>
      <div className="提示条">
        冒烟顺序：<Link to="/事件流">事件流</Link> 依次推三份样例 → 看水位线 / 热度窗 / 撤回单 / 旁路匣 →{" "}
        <Link to="/窗互证">窗互证</Link>。
      </div>
      <div className="行"><button className="次" onClick={刷}>刷新台面</button></div>
      {末 ? (
        <div className="行" style={{ gap: "0.7rem" }}>
          <span>最近窗互证</span>
          <span className={`徽章 ${末.是否通过 ? "通" : "败"}`}>{末.是否通过 ? "对齐" : "撕裂"}</span>
          <span className="讯" style={{ margin: 0 }}>{末.说明}</span>
        </div>
      ) : (
        <div className="空态">还没跑过窗互证。先推事件流，再去「窗互证」。</div>
      )}
    </div>
  );
}
