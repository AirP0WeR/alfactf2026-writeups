import { INTERPOLATION_DELAY } from '../../../shared/constants.js';

export class Interpolation {
  constructor() {
    this.snapshotBuffer = [];
    this.maxBufferSize = 20;
  }

  pushSnapshot(snapshot) {
    snapshot.receivedAt = performance.now();
    this.snapshotBuffer.push(snapshot);

    if (this.snapshotBuffer.length > this.maxBufferSize) {
      this.snapshotBuffer.shift();
    }
  }

  getInterpolatedState(renderTime) {
    const targetTime = renderTime - INTERPOLATION_DELAY;

    const buffer = this.snapshotBuffer;
    if (buffer.length < 2) {
      return buffer.length > 0 ? buffer[buffer.length - 1] : null;
    }

    let older = null;
    let newer = null;

    for (let i = 0; i < buffer.length - 1; i++) {
      if (buffer[i].receivedAt <= targetTime && buffer[i + 1].receivedAt >= targetTime) {
        older = buffer[i];
        newer = buffer[i + 1];
        break;
      }
    }

    if (!older || !newer) {
      return buffer[buffer.length - 1];
    }

    const range = newer.receivedAt - older.receivedAt;
    const t = range > 0 ? (targetTime - older.receivedAt) / range : 0;

    return this.interpolateSnapshots(older, newer, Math.max(0, Math.min(1, t)));
  }

  interpolateSnapshots(a, b, t) {
    const result = {
      tick: b.tick,
      state: b.state,
      score: b.score,
      players: [],
      ball: null,
      receivedAt: a.receivedAt + (b.receivedAt - a.receivedAt) * t
    };

    if (a.players && b.players) {
      for (const bp of b.players) {
        const ap = a.players.find(p => p.id === bp.id);
        if (ap) {
          result.players.push({
            ...bp,
            x: ap.x + (bp.x - ap.x) * t,
            y: ap.y + (bp.y - ap.y) * t,
            facing: this.lerpAngle(ap.facing, bp.facing, t)
          });
        } else {
          result.players.push(bp);
        }
      }
    }

    if (a.ball && b.ball) {
      result.ball = {
        ...b.ball,
        x: a.ball.x + (b.ball.x - a.ball.x) * t,
        y: a.ball.y + (b.ball.y - a.ball.y) * t,
        z: a.ball.z + (b.ball.z - a.ball.z) * t
      };
    } else {
      result.ball = b.ball;
    }

    return result;
  }

  lerpAngle(a, b, t) {
    let diff = b - a;
    
    while (diff > Math.PI) diff -= Math.PI * 2;
    while (diff < -Math.PI) diff += Math.PI * 2;
    return a + diff * t;
  }

  clear() {
    this.snapshotBuffer = [];
  }
}
