export interface TagHierarchy extends Record<string, TagHierarchy>{};
export const TAG_SEP = "->";

export class DataTags extends Set<string>{
    /* Remove spaces between words in a tag */
    static removeSpaces(tag: string): string{
        const splitTag = tag.split(TAG_SEP);
        for (let i = 0; i < splitTag.length; i++){
            splitTag[i] = splitTag[i].trim();
        }
        tag = splitTag.join(TAG_SEP);
        return tag;
    }
    constructor(tags: string[] | DataTags | Set<string> | null = null ){
        if (tags === null){
            tags = [];
        }
        // remove spaces between words
        const _tags = tags instanceof Set ? tags : new Set(tags);
        _tags.forEach((tag) => { return DataTags.removeSpaces(tag); })
        super(_tags);
    }
    copy(){
        return new DataTags(this);
    }
    equals(tags: DataTags){
        if (tags.size !== this.size){
            return false;
        }
        for (const tag of this){
            if (!tags.has(tag)){ return false; }
        }
        return true;
    }
    add(tag: string){
        return super.add(DataTags.removeSpaces(tag));
    }
    has(tag: string){
        return super.has(DataTags.removeSpaces(tag));
    }
    // @ts-ignore: Property 'union' in type 'DataTags' is not assignable to the same property in base type 'Set<string>'.
    // Type '(tags: DataTags) => DataTags' is not assignable to type '<U>(other: ReadonlySetLike<U>) => Set<string | U>'.
    // https://github.com/Microsoft/TypeScript/issues/22198#issuecomment-369278691
    union( tags: DataTags ): DataTags {
        const ret = new DataTags(this);
        ret.union_(tags);
        return ret;
    }
    union_(tags: DataTags){
        tags.forEach((value) => this.add(value));
        return this;
    }
    pop( tags: DataTags){
        const ret = new DataTags(this);
        ret.pop_(tags);
        return ret;
    }
    pop_(tags: DataTags){
        tags.forEach((value) => this.delete(value));
        return this;
    }
    pop_ifcontains_( tags: DataTags){
        tags.forEach((value)=>{ if (this.has(value)){ this.delete(value); } })
        return this;
    }
    issubset(tags: DataTags){
        return TagRule.isSubset(this, tags)
    }
    withParents():DataTags {
        const ret = new DataTags(this)
        this.forEach(tag => ret.union_(TagRule.allParentsOf(tag)));
        return ret;
    }
    withChildsFrom(tagPool: DataTags): DataTags{
        const ret = new DataTags(this);
        this.forEach((tag) => ret.union_(TagRule.allChildsOf(tag, tagPool)));
        return ret;
    }
    /* return all parents that has child in this */
    allParents(): DataTags{
        const ret = new DataTags()
        this.forEach(tag => ret.union_(TagRule.allParentsOf(tag)));
        return ret;
    }
    toArray(): string[]{
        return Array.from(this);
    }
}

export class TagRule {
    // assume cls.SEP is '.'
    // input: a.b.c
    // return: [a, a.b]
    static allParentsOf(tag: string): DataTags {
        const sp = tag.split(TAG_SEP);
        if (sp.length === 1) {
          return new DataTags([]);
        }
        const accum = [];
        const all_p_tags = [];
        for (let i = 0; i < sp.length - 1; i++) {
          accum.push(sp[i]);
          all_p_tags.push(accum.join(TAG_SEP));
        }
        return new DataTags(all_p_tags);
      }

    // assume cls.SEP is '.'
    // input: (a.b, [a, a.b, a.b.c, a.b.d])
    // return: [a.b.c, a.b.d]
    static allChildsOf(tag: string, tag_pool: DataTags): DataTags {
        const ret = new DataTags();
        for (const t of tag_pool) {
          if (t.startsWith(tag) && t.length > tag.length + TAG_SEP.length) {
            if (t.substring(tag.length, tag.length  + TAG_SEP.length) === `${TAG_SEP}`) {
              ret.add(t);
            }
          }
        }
        return ret;
    }

    static tagHierarchy(tags: DataTags): TagHierarchy{
        const SEP = TAG_SEP;

        function splitFirstElement(tag: string, sep: string): [string, string] | [string]{
            const splitted = tag.split(sep);
            if (splitted.length === 1) {return [tag]};
            return [splitted[0], splitted.slice(1, ).join(sep)]
        }

        // Turn a list of tags into TagHierarchy objects without parents
        function disassemble(tags: string[], sep: string = SEP): TagHierarchy{
            const interm: Record<string, string[]> = {}
            const splittedTags = tags.map((tag) => splitFirstElement(tag, sep))
            for (const st of splittedTags){
                if (!(st[0] in interm)){
                    interm[st[0]] = [];
                }
                if (st.length === 2){
                    interm[st[0]].push(st[1]);
                }
            }
            const res: TagHierarchy = {};
            for (const key in interm){
                res[key] = disassemble(interm[key], sep);
            }
            return res;
        }

        // Aggregately add parent portion of the hierarchy, in-place operation
        function assemble(disassembled: TagHierarchy, sep: string = SEP): TagHierarchy{
            for (const key in disassembled){
                const value = disassembled[key];
                for (const childKey in value){
                    const newKey = [key, childKey].join(SEP);
                    value[newKey] = value[childKey];
                    delete value[childKey];
                }
                assemble(value, sep);
            }
            return disassembled;
        }
        return assemble(disassemble(Array.from(tags)));
    }

    static isSubset(query: DataTags, value: DataTags): boolean{
        let flag = true;
        for (const q of query){
            if (!(value.has(q))){
                flag = false;
                break;
            }
        }
        return flag;
    }
}