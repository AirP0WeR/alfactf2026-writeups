import {
  COURT_WIDTH, NET_Y, SERVICE_LINE_DIST
} from '../../shared/constants.js';
import { SERVICE_BOXES } from '../../shared/CourtLayout.js';

export class ServeManager {
  constructor() {
    this.servingTeam = 0;
    this.servingPlayerIndex = 0;
    this.serveSide = 'deuce';
    this.faults = 0;
    this.state = 'idle';
    this.serveTimer = 0;
  }

  setupServe(servingTeam, servingPlayerIndex, serveSide) {
    this.servingTeam = servingTeam;
    this.servingPlayerIndex = servingPlayerIndex;
    this.serveSide = serveSide;
    this.faults = 0;
    this.state = 'ready';
    this.serveTimer = 0;
  }

  getServingPosition() {
    const team = this.servingTeam;
    const side = this.serveSide;

    let x, y;
    if (team === 0) {
      y = NET_Y - SERVICE_LINE_DIST - 50;
      x = side === 'deuce' ? COURT_WIDTH * 0.75 : COURT_WIDTH * 0.25;
    } else {
      y = NET_Y + SERVICE_LINE_DIST + 50;
      x = side === 'deuce' ? COURT_WIDTH * 0.25 : COURT_WIDTH * 0.75;
    }

    return { x, y };
  }

  getTargetBox() {
    
    const boxKey = this.serveSide;
    if (this.servingTeam === 0) {
      return SERVICE_BOXES.team1[boxKey];
    } else {
      return SERVICE_BOXES.team2[boxKey];
    }
  }

  validateServe(ball) {
    
    const box = this.getTargetBox();

    if (ball.bounceCount === 1 && ball.z <= 1) {
      const inBox = ball.x >= box.x1 && ball.x <= box.x2 &&
                    ball.y >= box.y1 && ball.y <= box.y2;

      if (inBox) {
        return 'good';
      } else {
        return 'fault';
      }
    }

    return 'pending';
  }

  recordFault() {
    this.faults++;
    if (this.faults >= 2) {
      return 'double_fault';
    }
    this.state = 'ready';
    return 'fault';
  }

  nextPoint() {
    
    this.serveSide = this.serveSide === 'deuce' ? 'ad' : 'deuce';
    this.faults = 0;
    this.state = 'ready';
  }

  nextGame(newServingTeam, newServingPlayerIndex) {
    this.servingTeam = newServingTeam;
    this.servingPlayerIndex = newServingPlayerIndex;
    this.serveSide = 'deuce';
    this.faults = 0;
    this.state = 'ready';
  }
}
