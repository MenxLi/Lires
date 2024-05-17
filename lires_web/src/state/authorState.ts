import { ref, watch, type Ref } from 'vue';
import { useConnectionStore } from "./store";

/**
 * @param authorNames The names of the authors to get papers for
 * @returns A reactive object containing the paper ids for each author, 
 * and a function to update the paper ids
 */
export function useAuthorPapers(
    authorNames: Ref<string[]>,
): {authorPapers: Ref<Record<string, string[]>>, updateAuthorPapers: () => void}
{
    const conn = useConnectionStore().conn;
    const authorPapers = ref({} as Record<string, string[]>);

    const updateAuthorPapers = () => {
        Promise.all(
            authorNames.value.map(
                (author) => conn.query({
                    searchBy: 'author',
                    searchContent: author,
                })
            )
        ).then(
            (res) => {
                for (let i = 0; i < authorNames.value.length; i++) {
                    authorPapers.value[authorNames.value![i]] = res[i].uids;
                }
            }
        );
    };

    watch(authorNames, updateAuthorPapers, {immediate: true});
    return {authorPapers, updateAuthorPapers};
}