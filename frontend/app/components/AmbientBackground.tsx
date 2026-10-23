import React from 'react';

export const AmbientBackground: React.FC = () => {
  return (
    <div className="ambient-container" aria-hidden="true">
      {/* Radiant ambient glow blur nodes */}
      <div className="ambient-orb orb-crimson-main" />
      <div className="ambient-orb orb-lime-main" />
      <div className="ambient-orb orb-peach-center" />
      <div className="ambient-orb orb-cyan-accent" />

      {/* Crisp glowing geometric toruses and refraction ribbons */}
      <div className="glow-torus torus-1" />
      <div className="glow-torus torus-2" />
      <div className="glass-ribbon" />
    </div>
  );
};
