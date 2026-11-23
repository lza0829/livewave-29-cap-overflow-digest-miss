import React from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import 热度台 from "./pages/热度台.jsx";
import 事件流 from "./pages/事件流.jsx";
import 水位线 from "./pages/水位线.jsx";
import 热度窗 from "./pages/热度窗.jsx";
import 撤回单 from "./pages/撤回单.jsx";
import 旁路匣 from "./pages/旁路匣.jsx";
import 窗互证 from "./pages/窗互证.jsx";
import 上限闸 from "./pages/上限闸.jsx";
import 窗参 from "./pages/窗参.jsx";
import 超额摘要 from "./pages/超额摘要.jsx";

const 主链 = [
  ["/", "热度台"],
  ["/事件流", "① 事件流"],
  ["/水位线", "② 水位线"],
  ["/热度窗", "③ 热度窗"],
  ["/撤回单", "④ 撤回单"],
  ["/旁路匣", "⑤ 旁路匣"],
  ["/窗互证", "窗互证"],
];
const 次链 = [["/上限闸", "上限闸"], ["/窗参", "窗参"]];

export default function App() {
  return (
    <div className="壳">
      <header className="顶栏">
        <div className="顶上行">
          <div className="牌名">播浪</div>
          <div className="牌骨">事件时抬水位 → 关热度窗 → 迟到撤回 / 超迟旁路 → 窗互证</div>
        </div>
        <nav className="管线">
          {主链.map(([to, l]) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => (isActive ? "亮" : "")}>
              {l}
            </NavLink>
          ))}
          {次链.map(([to, l]) => (
            <NavLink key={to} to={to} className={({ isActive }) => (isActive ? "亮 次链" : "次链")}>
              {l}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="主">
        <Routes>
          <Route path="/" element={<热度台 />} />
          <Route path="/事件流" element={<事件流 />} />
          <Route path="/水位线" element={<水位线 />} />
          <Route path="/热度窗" element={<热度窗 />} />
          <Route path="/撤回单" element={<撤回单 />} />
          <Route path="/旁路匣" element={<旁路匣 />} />
          <Route path="/窗互证" element={<窗互证 />} />
          <Route path="/上限闸" element={<上限闸 />} />
          <Route path="/窗参" element={<窗参 />} />
          <Route path="/超额摘要" element={<超额摘要 />} />
        </Routes>
      </main>
    </div>
  );
}
