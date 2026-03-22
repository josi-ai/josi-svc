'use client';

export function VedicChartIcon() {
  const signs = ['Pi','Ar','Ta','Ge','Aq',null,null,'Ca','Cp',null,null,'Le','Sg','Sc','Li','Vi'];
  return (
    <div className="w-[52px] h-[52px] aspect-square grid grid-cols-4 grid-rows-4" style={{ border: '1px solid rgba(200,145,58,0.3)' }}>
      {signs.map((sign, i) => {
        const isCenter = i === 5 || i === 6 || i === 9 || i === 10;
        const isAsc = i === 7; // Cancer
        if (isCenter) {
          if (i === 5) return (
            <div key={i} className="flex items-center justify-center" style={{ gridColumn: '2/4', gridRow: '2/4', background: 'rgba(200,145,58,0.04)', border: '1px solid rgba(200,145,58,0.15)' }}>
              <span style={{ fontSize: 6, color: '#5B6A8A' }}>Rasi</span>
            </div>
          );
          return null;
        }
        return (
          <div key={i} className="flex items-center justify-center" style={{ border: '1px solid rgba(200,145,58,0.12)', background: isAsc ? 'rgba(200,145,58,0.15)' : 'transparent' }}>
            <span style={{ fontSize: 6, color: isAsc ? '#C8913A' : '#5B6A8A' }}>{sign}</span>
          </div>
        );
      })}
    </div>
  );
}

export function WesternChartIcon() {
  return (
    <div className="w-[52px] h-[52px] aspect-square rounded-full relative" style={{ border: '1.5px solid rgba(106,159,216,0.35)', background: 'rgba(106,159,216,0.03)' }}>
      {/* Inner circle */}
      <div className="absolute rounded-full" style={{ width: 26, height: 26, top: '50%', left: '50%', transform: 'translate(-50%,-50%)', border: '1px solid rgba(106,159,216,0.15)' }} />
      {Array.from({length:12}).map((_,i) => (
        <div key={i} className="absolute" style={{ width: 1, height: '50%', background: 'rgba(106,159,216,0.2)', left: '50%', top: 0, transformOrigin: '50% 100%', transform: `translateX(-0.5px) rotate(${i*30}deg)` }} />
      ))}
      {[
        {angle:40,dist:18,color:'#C8913A'},
        {angle:130,dist:16,color:'#6A9FD8'},
        {angle:250,dist:20,color:'#E08060'},
        {angle:310,dist:15,color:'#9678C8'},
      ].map((p,i) => {
        const rad = (p.angle * Math.PI) / 180;
        const x = 26 + p.dist * Math.cos(rad);
        const y = 26 + p.dist * Math.sin(rad);
        return <div key={i} className="absolute rounded-full" style={{ width: 3, height: 3, background: p.color, left: x, top: y, transform: 'translate(-50%,-50%)', boxShadow: `0 0 3px ${p.color}` }} />;
      })}
    </div>
  );
}

export function ChineseChartIcon() {
  const pillars = [
    { stem: '\u58EC', branch: '\u7533' },
    { stem: '\u7678', branch: '\u536F' },
    { stem: '\u4E19', branch: '\u5348' },
    { stem: '\u7532', branch: '\u5B50' },
  ];
  return (
    <div className="w-[52px] h-[52px] aspect-square flex items-center justify-center gap-1">
      {pillars.map((p, i) => (
        <div key={i} className="flex flex-col items-center gap-0.5">
          <div className="w-[12px] h-[16px] rounded-sm flex items-center justify-center" style={{ border: '1px solid rgba(224,128,96,0.3)', background: 'rgba(224,128,96,0.06)' }}>
            <span style={{ fontSize: 8, color: '#E08060' }}>{p.stem}</span>
          </div>
          <div className="w-[12px] h-[16px] rounded-sm flex items-center justify-center" style={{ border: '1px solid rgba(224,128,96,0.2)', background: 'rgba(224,128,96,0.03)' }}>
            <span style={{ fontSize: 8, color: '#E08060' }}>{p.branch}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export function HellenisticChartIcon() {
  return (
    <div className="w-[52px] h-[52px] aspect-square rounded-full relative" style={{ border: '1.5px solid rgba(150,120,200,0.35)', background: 'rgba(150,120,200,0.03)' }}>
      {Array.from({length:12}).map((_,i) => (
        <div key={i} className="absolute" style={{ width: 1, height: '50%', background: 'rgba(150,120,200,0.25)', left: '50%', top: 0, transformOrigin: '50% 100%', transform: `translateX(-0.5px) rotate(${i*30}deg)` }} />
      ))}
      {/* Central dot */}
      <div className="absolute rounded-full" style={{ width: 6, height: 6, background: 'rgba(150,120,200,0.4)', top: '50%', left: '50%', transform: 'translate(-50%,-50%)' }} />
      {/* Two planet markers */}
      {[{angle:60,dist:18},{angle:200,dist:16}].map((p,i) => {
        const rad = (p.angle * Math.PI) / 180;
        return <div key={i} className="absolute rounded-full" style={{ width: 3, height: 3, background: '#9678C8', left: 26 + p.dist * Math.cos(rad), top: 26 + p.dist * Math.sin(rad), transform: 'translate(-50%,-50%)', boxShadow: '0 0 3px #9678C8' }} />;
      })}
    </div>
  );
}

export function MayanChartIcon() {
  return (
    <div className="w-[52px] h-[52px] aspect-square flex items-center justify-center">
      <div className="grid grid-cols-5 grid-rows-4 gap-[2px]">
        {Array.from({length:20}).map((_,i) => (
          <div key={i} className="rounded-full" style={{ width: 6, height: 6, background: i === 7 ? '#50B8D0' : `rgba(80,184,208,${0.1 + (i % 5) * 0.08})`, border: i === 7 ? '1px solid #50B8D0' : '1px solid rgba(80,184,208,0.2)' }} />
        ))}
      </div>
    </div>
  );
}

export function CelticChartIcon() {
  return (
    <div className="w-[52px] h-[52px] aspect-square rounded-full relative" style={{ border: '1.5px solid rgba(106,176,122,0.35)', background: 'rgba(106,176,122,0.03)' }}>
      {/* 13 division lines */}
      {Array.from({length:13}).map((_,i) => (
        <div key={i} className="absolute" style={{ width: 1, height: '50%', background: 'rgba(106,176,122,0.2)', left: '50%', top: 0, transformOrigin: '50% 100%', transform: `translateX(-0.5px) rotate(${i * (360/13)}deg)` }} />
      ))}
      {/* Tree trunk in center */}
      <div className="absolute" style={{ width: 2, height: 16, background: 'rgba(106,176,122,0.4)', left: '50%', top: '35%', transform: 'translateX(-50%)' }} />
      {/* Tree branches */}
      <div className="absolute" style={{ width: 12, height: 2, background: 'rgba(106,176,122,0.3)', left: '50%', top: '38%', transform: 'translate(-50%) rotate(30deg)' }} />
      <div className="absolute" style={{ width: 10, height: 2, background: 'rgba(106,176,122,0.3)', left: '50%', top: '42%', transform: 'translate(-50%) rotate(-25deg)' }} />
    </div>
  );
}
