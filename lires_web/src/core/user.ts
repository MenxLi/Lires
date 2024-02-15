import type { ServerConn } from '../api/serverConn';
import type { UserInfo } from '../api/protocalT';


export class User{
    conn: ServerConn;
    info: UserInfo;

    constructor(conn: ServerConn, info: UserInfo){
        this.conn = conn;
        this.info = info;
    }

    get baseURL(): string{
        return this.conn.baseURL;
    }

    avatarURL(size: number = 128, t: number | null = -1): string{
        let tStamp;
        if(t === null){ tStamp = ''; }
        else if (t < 0){ tStamp = `&t=${Date.now()}`; }
        else{ tStamp = `&t=${t}`; }
        return `${this.baseURL}/user-avatar/${this.info.username}?size=${size}${tStamp}`
    }

}


export class UserPool{
    conn: ServerConn;
    constructor(conn: ServerConn){
        this.conn = conn;
    }
    async list(): Promise<User[]>{
        let userInfoList = await this.conn.reqUserList();
        return userInfoList.map(v => new User(this.conn, v));
    }
    async get(username: string): Promise<User>{
        let userInfo = await this.conn.reqUserInfo(username);
        return new User(this.conn, userInfo);
    }
}