// 書き順判定の合成テスト。
// 使い方: python3 -m http.server 8781 --directory dist で開いたページの、ブラウザの開発者コンソールに貼って実行する。
// お手本の画を、拡大縮小・回転・せん断・画ごとのずれ・ゆれで崩した「こどもっぽい字」を作り、
//   1) 正しい文字として受け入れられる割合
//   2) 画数が同じ別の文字として受け入れてしまう件数(取りちがえ)
//   3) 書き順の入れかえ・画の向きの逆転を見つけられる割合
// を出す。しきい値(window.__hira.TH)を変えたら、取りちがえが 0 のままか必ず確認する。
(() => {
  const H = window.__hira;
  const rnd = a => (Math.random() * 2 - 1) * a;
  function kid(ch, amt = 1) {
    const raw = H.TPL[ch].raw, b = H.TPL[ch].box, cx = b.x0 + b.w / 2, cy = b.y0 + b.h / 2;
    const sx = 1 + rnd(.15 * amt), sy = 1 + rnd(.15 * amt), rot = rnd(.12 * amt), sh = rnd(.12 * amt);
    return raw.map(s => {
      const ox = rnd(.06 * amt) * b.size, oy = rnd(.06 * amt) * b.size, ss = 1 + rnd(.15 * amt);
      const scx = s.reduce((a, p) => a + p[0], 0) / s.length, scy = s.reduce((a, p) => a + p[1], 0) / s.length;
      const ph = Math.random() * 6, wob = .025 * amt * b.size;
      return s.map((p, i) => {
        let x = scx + (p[0] - scx) * ss + ox - cx, y = scy + (p[1] - scy) * ss + oy - cy;
        let X = x * sx + y * sh, Y = y * sy;
        const c = Math.cos(rot), si = Math.sin(rot);
        [X, Y] = [X * c - Y * si, X * si + Y * c];
        X += Math.sin(i * .4 + ph) * wob; Y += Math.cos(i * .33 + ph) * wob;
        return [(X + cx) * 4, (Y + cy) * 4];
      });
    });
  }
  const out = {};
  for (const amt of [0.7, 1.0, 1.4]) {
    let ok = 0, n = 0;
    for (const ch of H.ALL) for (let k = 0; k < 8; k++) { n++; if (H.recognize(kid(ch, amt), ch, { boxSize: 400 }).ok) ok++; }
    out[`受け入れ(崩し ${amt})`] = `${ok}/${n}`;
  }
  let fa = 0, fn = 0; const pairs = new Set();
  for (const a of H.ALL) for (const b of H.ALL) {
    if (a === b || H.TPL[a].raw.length !== H.TPL[b].raw.length) continue;
    for (let k = 0; k < 3; k++) { fn++; if (H.recognize(kid(a, 1.2), b, { boxSize: 400 }).ok) { fa++; pairs.add(`${a}→${b}`); } }
  }
  out['取りちがえ'] = `${fa}/${fn} ${[...pairs].join(' ')}`;
  let od = 0, on = 0, dd = 0, dn = 0;
  for (const ch of H.ALL) {
    const n = H.TPL[ch].raw.length;
    if (n >= 2) for (let k = 0; k < 4; k++) {
      const s = kid(ch, .8), i = Math.floor(Math.random() * (n - 1));
      [s[i], s[i + 1]] = [s[i + 1], s[i]]; on++;
      if (H.recognize(s, ch, { boxSize: 400 }).reason === 'order') od++;
    }
    const cand = H.TPL[ch].lens.map((l, i) => l > .4 ? i : -1).filter(i => i >= 0);
    if (cand.length) for (let k = 0; k < 3; k++) {
      const s = kid(ch, .8), i = cand[Math.floor(Math.random() * cand.length)];
      s[i] = s[i].slice().reverse(); dn++;
      if (H.recognize(s, ch, { boxSize: 400 }).reason === 'direction') dd++;
    }
  }
  out['書き順ちがいの検出'] = `${od}/${on}`;
  out['向きちがいの検出'] = `${dd}/${dn}`;
  console.table(out);
  return out;
})();
