import { reactive, toRefs, type Ref } from 'vue';

interface WindowState {
    width: number;
    height: number;
}

export function useWindowState(): { width: Ref<number>; height: Ref<number>; cleanup: () => void } {
    const state: WindowState = reactive({
        width: window.innerWidth,
        height: window.innerHeight,
    });

    function handleResize() {
        state.width = window.innerWidth;
        state.height = window.innerHeight;
    }

    // Attach event listener to window resize event
    window.addEventListener('resize', handleResize);

    // Cleanup function to remove event listener when component is unmounted
    // You can call this function in the `beforeUnmount` lifecycle hook
    function cleanup() {
        window.removeEventListener('resize', handleResize);
    }

    // Return the reactive state object as well as the cleanup function
    return {
        ...toRefs(state),
        cleanup,
    };
}