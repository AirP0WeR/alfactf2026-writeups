
const RECENT_CAP = 50;
const MATCH_TTL_SECONDS = 60 * 60 * 24 * 7;

export class MatchHistory {
  constructor(redis) {
    this.redis = redis;
  }

  async saveMatch({ roomId, roomName, winner, score, team1, team2, startedAt, endedAt }) {
    const id = `${roomId}_${endedAt}`;
    const durationMs = endedAt - startedAt;
    const payload = {
      id,
      roomId: String(roomId || ''),
      roomName: String(roomName || 'Padel Match'),
      winner: String(winner ?? ''),
      score: JSON.stringify(score || {}),
      team1: JSON.stringify(team1 || []),
      team2: JSON.stringify(team2 || []),
      startedAt: String(startedAt),
      endedAt: String(endedAt),
      durationMs: String(durationMs),
    };
    const pipe = this.redis.pipeline();
    pipe.hset(`match:${id}`, payload);
    pipe.expire(`match:${id}`, MATCH_TTL_SECONDS);
    pipe.lpush('matches:recent', id);
    pipe.ltrim('matches:recent', 0, RECENT_CAP - 1);
    pipe.incr('stats:matches_played');
    await pipe.exec();
    return id;
  }

  async getRecentMatches(limit = 10) {
    const n = Math.min(limit, RECENT_CAP);
    const ids = await this.redis.lrange('matches:recent', 0, n - 1);
    if (ids.length === 0) return [];
    const pipe = this.redis.pipeline();
    for (const id of ids) pipe.hgetall(`match:${id}`);
    const results = await pipe.exec();
    return results
      .map(([err, data]) => (err || !data || !data.id) ? null : this._deserialize(data))
      .filter(Boolean);
  }

  _deserialize(data) {
    return {
      id: data.id,
      roomId: data.roomId,
      roomName: data.roomName,
      winner: data.winner ? parseInt(data.winner, 10) : null,
      score: this._safeParse(data.score, {}),
      team1: this._safeParse(data.team1, []),
      team2: this._safeParse(data.team2, []),
      startedAt: parseInt(data.startedAt || '0', 10),
      endedAt: parseInt(data.endedAt || '0', 10),
      durationMs: parseInt(data.durationMs || '0', 10),
    };
  }

  _safeParse(s, fallback) {
    try { return JSON.parse(s); } catch { return fallback; }
  }
}
