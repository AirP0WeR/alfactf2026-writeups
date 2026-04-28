export class ScoringSystem {
  constructor() {
    this.reset();
  }

  reset() {
    this.sets = [];
    this.currentSet = 0;
    this.games = [0, 0];
    this.points = [0, 0];
    this.isDeuce = false;
    this.advantage = null;
    this.isTiebreak = false;
    this.tiebreakPoints = [0, 0];
    this.servingTeam = 0;
    this.servingPlayerIndex = 0;
    this.matchOver = false;
    this.winner = null;
    this.bestOf = 3;
  }

  scorePoint(team) {
    if (this.matchOver) return null;

    const result = { team, type: 'point' };

    if (this.isTiebreak) {
      return this.scoreTiebreakPoint(team);
    }

    if (this.isDeuce) {
      if (this.advantage === null) {
        
        this.advantage = team;
        result.display = 'Advantage';
      } else if (this.advantage === team) {
        
        return this.scoreGame(team);
      } else {
        
        this.advantage = null;
        result.display = 'Deuce';
      }
    } else {
      this.points[team]++;
      if (this.points[0] >= 3 && this.points[1] >= 3) {
        
        this.isDeuce = true;
        this.advantage = null;
        result.display = 'Deuce';
      } else if (this.points[team] >= 4) {
        
        return this.scoreGame(team);
      } else {
        const pointLabels = ['0', '15', '30', '40'];
        result.display = `${pointLabels[this.points[0]]} - ${pointLabels[this.points[1]]}`;
      }
    }

    return result;
  }

  scoreGame(team) {
    this.games[team]++;
    this.points = [0, 0];
    this.isDeuce = false;
    this.advantage = null;

    this.servingTeam = this.servingTeam === 0 ? 1 : 0;
    
    if ((this.games[0] + this.games[1]) % 2 === 0) {
      this.servingPlayerIndex = this.servingPlayerIndex === 0 ? 1 : 0;
    }

    const result = { team, type: 'game', games: [...this.games] };

    if (this.games[team] >= 6) {
      const other = team === 0 ? 1 : 0;
      if (this.games[team] - this.games[other] >= 2) {
        return this.scoreSet(team);
      } else if (this.games[0] === 6 && this.games[1] === 6) {
        
        this.isTiebreak = true;
        this.tiebreakPoints = [0, 0];
        result.tiebreak = true;
      }
    }

    result.display = `Game - Team ${team + 1}`;
    return result;
  }

  scoreTiebreakPoint(team) {
    this.tiebreakPoints[team]++;
    const result = { team, type: 'tiebreak_point', tiebreakPoints: [...this.tiebreakPoints] };

    const totalPoints = this.tiebreakPoints[0] + this.tiebreakPoints[1];
    if (totalPoints === 1 || (totalPoints > 1 && (totalPoints - 1) % 2 === 0)) {
      this.servingTeam = this.servingTeam === 0 ? 1 : 0;
    }

    if (this.tiebreakPoints[team] >= 7) {
      const other = team === 0 ? 1 : 0;
      if (this.tiebreakPoints[team] - this.tiebreakPoints[other] >= 2) {
        this.games[team]++;
        this.isTiebreak = false;
        this.tiebreakPoints = [0, 0];
        return this.scoreSet(team);
      }
    }

    result.display = `Tiebreak: ${this.tiebreakPoints[0]} - ${this.tiebreakPoints[1]}`;
    return result;
  }

  scoreSet(team) {
    this.sets.push([...this.games]);
    this.currentSet++;
    this.games = [0, 0];
    this.points = [0, 0];
    this.isDeuce = false;
    this.advantage = null;
    this.isTiebreak = false;
    this.tiebreakPoints = [0, 0];

    const result = {
      team,
      type: 'set',
      sets: this.sets.map(s => [...s]),
      display: `Set ${this.currentSet} - Team ${team + 1}`
    };

    const setsWon = [0, 0];
    for (const set of this.sets) {
      if (set[0] > set[1]) setsWon[0]++;
      else setsWon[1]++;
    }

    const setsNeeded = Math.ceil(this.bestOf / 2);
    if (setsWon[team] >= setsNeeded) {
      this.matchOver = true;
      this.winner = team;
      result.type = 'match';
      result.display = `Match - Team ${team + 1} wins!`;
    }

    return result;
  }

  serialize() {
    return {
      sets: this.sets.map(s => [...s]),
      games: [...this.games],
      points: [...this.points],
      isDeuce: this.isDeuce,
      advantage: this.advantage,
      isTiebreak: this.isTiebreak,
      tiebreakPoints: [...this.tiebreakPoints],
      servingTeam: this.servingTeam,
      servingPlayerIndex: this.servingPlayerIndex,
      matchOver: this.matchOver,
      winner: this.winner
    };
  }
}
