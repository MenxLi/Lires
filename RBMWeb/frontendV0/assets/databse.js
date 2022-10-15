class DataBase{
    constructor(allData){
        this.db = allData;
    }

    *[Symbol.iterator](){
        for (let d of this.db){
            yield d;
        }
    }

    getDataKeys = function(){
        return Array.from(Object.keys(this.db[0]))
    }

    getAllTags = function(){
        let _tags;
        let all_tags = new Set();
        for (const data of this.db){
            _tags = data["tags"];;
            for (const t of _tags){
                all_tags.add(t);
            }
        }
        return all_tags;
    }

    getDataByTags = function(tags){
        const valid_data = [];
        for (const data of this.db){
            const data_tag = data["tags"];
            if (isSubset(tags, data_tag)) {
                valid_data.push(data)
            }
        }
        return valid_data;
    }

    getDataByUUID = function(uuid){
        for (const data of this.db){
            if (data["uuid"] === uuid){
                return data
            }
        }
        return null;
    }
}

function isSubset(query, value){
    let flag = true;
    for (const q of query){
        if (!(value.includes(q))){
            flag = false;
            break;
        }
    }
    return flag;
}


export {DataBase}
