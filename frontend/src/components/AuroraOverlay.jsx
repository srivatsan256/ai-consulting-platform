import React from "react";
import { motion } from "motion/react";
import "./AuroraOverlay.css";

const BLOBS = [
  { size: 520, x: "6%", y: "-10%", color: "rgba(124,58,237,0.55)", duration: 16, delay: 0 },
  { size: 460, x: "70%", y: "5%", color: "rgba(217,70,239,0.45)", duration: 20, delay: 2 },
  { size: 420, x: "50%", y: "60%", color: "rgba(34,211,238,0.4)", duration: 18, delay: 4 },
  { size: 380, x: "10%", y: "65%", color: "rgba(59,130,246,0.45)", duration: 22, delay: 1 },
  { size: 300, x: "85%", y: "70%", color: "rgba(168,85,247,0.4)", duration: 14, delay: 3 },
];

export default function AuroraOverlay() {
  return (
    <div className="aurora-root" aria-hidden="true">
      {BLOBS.map((blob, i) => (
        <motion.div
          key={i}
          className="aurora-blob"
          style={{
            width: blob.size,
            height: blob.size,
            left: blob.x,
            top: blob.y,
            background: `radial-gradient(circle, ${blob.color}, transparent 70%)`,
          }}
          animate={{ x: [0, 40, -30, 0], y: [0, -30, 25, 0], scale: [1, 1.15, 0.92, 1] }}
          transition={{ duration: blob.duration, repeat: Infinity, ease: "easeInOut", delay: blob.delay }}
        />
      ))}
    </div>
  );
}
