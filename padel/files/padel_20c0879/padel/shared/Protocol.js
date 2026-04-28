
export const C_JOIN = 'c_join';
export const C_READY = 'c_ready';
export const C_INPUT = 'c_input';
export const C_SHOT = 'c_shot';
export const C_PING = 'c_ping';
export const C_CREATE_ROOM = 'c_create_room';
export const C_LIST_ROOMS = 'c_list_rooms';
export const C_CHAT = 'c_chat';
export const C_START_GAME = 'c_start_game';
export const C_SERVE_TOSS = 'c_serve_toss';
export const C_SERVE_HIT = 'c_serve_hit';
export const C_USER_KICK = 'c_user_kick';
export const C_ADMIN_UPDATE_SETTINGS = 'c_admin_update_settings';
export const C_ADMIN_CLOSE_ROOM = 'c_admin_close_room';
export const C_LIST_OFFICIAL = 'c_list_official';
export const C_LEAVE_ROOM = 'c_leave_room';
export const C_UNREADY = 'c_unready';
export const C_REQUEST_HOSTING_NAME = 'c_request_hosting_name';

export const S_ROOM_STATE = 's_room_state';
export const S_ROOM_LIST = 's_room_list';
export const S_MATCH_START = 's_match_start';
export const S_SNAPSHOT = 's_snapshot';
export const S_POINT_SCORED = 's_point_scored';
export const S_SET_WON = 's_set_won';
export const S_MATCH_END = 's_match_end';
export const S_PONG = 's_pong';
export const S_INPUT_ACK = 's_input_ack';
export const S_ERROR = 's_error';
export const S_WELCOME = 's_welcome';
export const S_CHAT = 's_chat';
export const S_REDIRECT = 's_redirect';
export const S_RECENT_MATCHES = 's_recent_matches';
export const S_KICKED = 's_kicked';
export const S_OFFICIAL_LIST = 's_official_list';
export const S_HOSTING_NAME = 's_hosting_name';

export const C_LIST_MATCHES = 'c_list_matches';

export function encode(msg) {
  return JSON.stringify(msg);
}

export function decode(data) {
  return JSON.parse(data);
}
