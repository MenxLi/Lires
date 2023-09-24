
<script setup lang="ts">
    import Plot3d from './Plot3d.vue';
    import LoadingWidget from '../common/LoadingWidget.vue';
    import { ref, computed } from 'vue';
    import { useDataStore, useUIStateStore, useSettingsStore } from '../store';
    import { ServerConn } from '../../core/serverConn';
    import { deepCopy } from '../../core/misc';
    import { ThemeMode } from '../../core/misc';
    import type { DatabaseFeature } from '../../core/protocalT';
    import type { PlotPoints3D } from '../interface';

    const dataStore = useDataStore();
    const plot3DRef = ref(null as any);
    const uiState = useUIStateStore();
    const settingsStore = useSettingsStore();

    const featsRaw = ref(null as null | DatabaseFeature);
    const feats = computed(()=>{
        if (featsRaw.value === null){
            return {};
        }
        // filter out the features that are not in the database
        const allUIDs = Object.keys(dataStore.database.data);
        const ret = {} as DatabaseFeature;
        for (const uid of allUIDs){
            if (featsRaw.value[uid]){
                // make sure the feature is from the database
                ret[uid] = featsRaw.value[uid];
            }
        }
        return ret;
    })

    // uids: the uids of the data to be shown
    function getPointsGroupFromUids(
        uids: string[], 
        colors: string | string[] | number[] = 'rgb(100, 100, 200)'
        ): PlotPoints3D{
        const feats_ = feats.value;
        if (!feats_){
            // features not ready
            uids = [];
        }
        else{
            // console.log("before filter", uids.length)
            for (let i=uids.length-1; i>=0; i--){
                if (feats_[uids[i]] === undefined){
                    // make sure the data with the uid is featurized
                    uids.splice(i, 1);
                }
            }
            // console.log("after filter", uids.length)
        }

        const len = uids.length;
        const xs = new Float32Array(len);
        const ys = new Float32Array(len);
        const zs = new Float32Array(len);
        const texts = new Array<string>(len);
        for (const [i, uid] of uids.entries()){
            let feat = feats_[uid];
            if (feat == undefined){
                throw new Error("uid not found in feats: " + uid);
            }
            xs[i] = feat[0];
            ys[i] = feat[1];
            zs[i] = feat[2];
            const dp = dataStore.database.get(uid);
            texts[i] = `${dp.authorYear()}<br>${dp.summary.title}`;
        };
        let color;
        if (typeof colors == 'string'){
            color = colors;
        }
        else if (colors instanceof Array){
            if (typeof colors[0] == 'string'){
                color = colors as string[];
            }
            else{
                // scores to colors
                const scores = colors as number[];
                const maxScore = Math.max(...scores);
                const minScore = Math.min(...scores);
                const scl = {
                    0: ThemeMode.isDarkMode()? [50, 50, 50]:[220, 220, 220],
                    1: [50, 200, 150]
                };
                const c = scores.map((s)=>{
                    const ratio = (s - minScore) / (maxScore - minScore);
                    const color = Array<number>(3);
                    for (let i =0; i< 3 ; i++){
                        color[i] = Math.round(scl[0][i] * (1 - ratio) + scl[1][i] * ratio);
                    }
                    return `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
                })
                color = c;
            }
        }
        else{
            throw new Error("Invalid color type");
        }
        return {
            x: xs,
            y: ys,
            z: zs,
            opacity: .75,
            color: color,
            text: texts,
        } as PlotPoints3D
    }

    const plotPoints = computed(()=>{
        const scores = uiState.shownDataScores;
        let shownPoints;
        if (scores){
            shownPoints = getPointsGroupFromUids(deepCopy(uiState.shownDataUIDs), scores);
        }
        else{
            shownPoints = getPointsGroupFromUids(deepCopy(uiState.shownDataUIDs));    // must use deepCopy here!
        }
        const allUIDs = Object.keys(dataStore.database.data);
        const remainUIDs = allUIDs.filter((uid)=>uiState.shownDataUIDs.indexOf(uid) == -1);

        const remainPoints = getPointsGroupFromUids(remainUIDs, 
            ThemeMode.isDarkMode()?'rgb(50, 50, 50)': 'rgb(220, 220, 220)'
        );
        const selectedPoints = getPointsGroupFromUids(deepCopy(uiState.unfoldedDataUIDs), 'rgb(255, 0, 0)');
        return [shownPoints, remainPoints, selectedPoints];
    }
    )

    const dataObtained = computed(()=>{
        return Object.keys(feats.value).length > 0;
    })
    async function fetchFeaturess(){
        featsRaw.value = null;
        const datasetSize = (await new ServerConn().status()).n_data;

        // set perplextiy to according to the dataset size
        let perp;
        if (datasetSize < 50){ perp = -1; }    // use PCA
        else if (datasetSize < 100){ perp = 5; }
        else if (datasetSize < 300) { perp = 8; }
        else if (datasetSize < 500) { perp = 12; }
        else{ perp = 15; }

        console.log("dataset size: ", datasetSize, "perp: ", perp);

        new ServerConn().reqDatabaseFeatureTSNE("doc_feature", 3, perp).then((data)=>{
            featsRaw.value = data;
        });
    }
    function onToggleDetail(ev:Event){
        if (ev.target instanceof HTMLDetailsElement){
            if (ev.target.open){
                settingsStore.setShow3DScatterPlot(true);
                fetchFeaturess();
            }
            else{
                settingsStore.setShow3DScatterPlot(false);
            }
        }
    }

</script>

<template>
    <div id="main">
        <details @toggle="onToggleDetail" :open="settingsStore.show3DScatterPlot">
            <summary>Visualization</summary>
            <div id="plot3dDiv">
                <Plot3d :data="plotPoints" ref="plot3DRef"></Plot3d>
                <div id="loadingDiv" class="full" v-if="!dataObtained">
                    <LoadingWidget v-if="featsRaw === null"></LoadingWidget>
                    <p class="status" v-else>Data not ready</p>
                </div>
            </div>
        </details>
    </div>
</template>

<style scoped>
    div#main{
        display: flex;
        margin-top: 0px;
        width: 100%;
        height: 100%;
    }

    details{
        margin: 0px;
        padding: 0px;
    }
    summary{
        font-weight: bold;
        margin-left: 10px;
    }

    .full{
        width: 100%;
        height: 100%;
    }

    div#plot3dDiv{
        height: 430px;
        width: 100%;
        max-width: 98vw;
        overflow: hidden;
        border-radius: 10px;
        z-index: 0;
        box-shadow: 0 0 2px var(--color-shadow);
    }
    div#loadingDiv{
        position:absolute;
        z-index: 1;
        top: 0px;
        left: 0px;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
    }
    
    div#loadingDiv p.status{
        font-size: large;
        font-weight: bold;
    }

    @media screen and (max-height: 900px) {
        div#plot3dDiv{
            height: 260px;
        }
    }
</style>