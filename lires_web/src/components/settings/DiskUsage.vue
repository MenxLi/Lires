<template>
    <div id="disk-usage-main">
        <div class="disk-usage-bar">
            <div class="disk-usage-fill" :style="{ width: fillPercentage }"></div>
        </div>
        <div class="disk-usage-text">
            Space: {{ usedSpace }} / {{ totalSpace }} {{ unit }}
        </div>
    </div>
</template>

<script>
import { useConnectionStore } from '../store';
export default {
    data() {
        return {
            usedSpace: 0,
            totalSpace: 1,
            unit: "MB",
        };
    },
    computed: {
        fillPercentage() {
            return `${Math.min(this.usedSpace / this.totalSpace, 1) * 100}%`;
        },
    },
    mounted() {
        // reset the disk usage
        this.usedSpace = 0;
        this.totalSpace = 1;
        this.unit = "MB";
        this.fetchDiskUsage();
    },
    methods: {
        fetchDiskUsage() {
            useConnectionStore().conn.reqDatabaseUsage().then(
                (usage) => {
                    const usedSpace = (usage.disk_usage / 1024 / 1024).toFixed(1);
                    const totalSpace = (usage.disk_limit / 1024 / 1024).toFixed(1);

                    if (totalSpace > 1024) {
                        this.unit = "GB";
                        this.usedSpace = (usedSpace / 1024).toFixed(1);
                        this.totalSpace = (totalSpace / 1024).toFixed(1);
                    } else {
                        this.unit = "MB";
                        this.usedSpace = usedSpace;
                        this.totalSpace = totalSpace;
                    }
                },
                () => {
                    console.log("failed to fetch disk usage");
                },
            );
        },
    },
};
</script>

<style scoped>
#disk-usage-main {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    /* padding-inline: 1rem; */
    gap: 0rem;
    width: 100%;
    height: 100%;
    overflow-y: auto;
}

.disk-usage-bar {
    width: 100%;
    height: 1rem;
    background-color: var(--color-background-progressbar);
    border-radius: 5px;
    overflow: hidden;
}

.disk-usage-fill {
    height: 100%;
    background-color: var(--color-progressbar);
    transition: width 0.3s ease-in-out;
}

.disk-usage-text {
    font-size: 0.75rem;
    text-align: center;
    height: 100%;
    color: var(--color-text-soft);
    white-space: nowrap;
}
</style>