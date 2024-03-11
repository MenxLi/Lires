
<script setup lang="ts">
    import Plot3d from './Plot3d.vue';
    import LoadingWidget from '../common/LoadingWidget.vue';
    import { ref, computed, watch, onMounted } from 'vue';
    import { useConnectionStore, useDataStore, useUIStateStore, useSettingsStore } from '../store';
    import { deepCopy } from '../../core/misc';
    import { ThemeMode } from '../../core/misc';
    import type { DatabaseFeature } from '../../api/protocalT';
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
        const allUIDs = dataStore.database.allKeys();
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
    async function getPointsGroupFrom(
        uids: string[], 
        colors: string | string[] | number[] = 'rgb(100, 100, 200)'
    ): Promise<PlotPoints3D>{
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
        const datapoints = await dataStore.database.agetMany(uids);
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
            const dp = datapoints[i];
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

    const plotPoints = ref(null as null | [PlotPoints3D, PlotPoints3D, PlotPoints3D]);
    async function updatePlotPoints(){
        const scores = uiState.shownDataScores;
        let shownPoints;
        if (scores){
            shownPoints = await getPointsGroupFrom(deepCopy(uiState.shownDataUIDs), scores);
        }
        else{
            shownPoints = await getPointsGroupFrom(deepCopy(uiState.shownDataUIDs));    // must use deepCopy here!
        }
        const allUIDs = dataStore.database.allKeys();
        const remainUIDs = allUIDs.filter((uid)=>uiState.shownDataUIDs.indexOf(uid) == -1);

        const remainPoints = await getPointsGroupFrom(remainUIDs, 
            ThemeMode.isDarkMode()?'rgb(50, 50, 50)': 'rgb(220, 220, 220)'
        );
        const selectedPoints = await getPointsGroupFrom(deepCopy(uiState.unfoldedDataUIDs), 'rgb(255, 0, 0)');
        plotPoints.value = [shownPoints, remainPoints, selectedPoints];
    }
    const dataObtained = computed(()=>{
        return Object.keys(feats.value).length > 0;
    })
    async function fetchFeaturess(){
        featsRaw.value = null;
        const conn = useConnectionStore().conn;
        const datasetSize = (await conn.status()).n_data;

        // set perplextiy to according to the dataset size
        let perp;
        if (datasetSize < 50){ perp = -1; }    // use PCA
        else if (datasetSize < 100){ perp = 5; }
        else if (datasetSize < 300) { perp = 8; }
        else if (datasetSize < 500) { perp = 12; }
        else{ perp = 15; }

        console.log("dataset size: ", datasetSize, "perp: ", perp);
        featsRaw.value = await conn.reqDatabaseFeatureTSNE("doc_feature", 3, perp);
    }

    
    watch(()=>[uiState.shownDataUIDs, uiState.unfoldedDataUIDs], ()=>{
        updatePlotPoints();
    })
    watch(()=>settingsStore.show3DScatterPlot, (v)=>{
        if (v){
            fetchFeaturess().then(()=>{
                updatePlotPoints();
            })
        }
    })
    onMounted(()=>{
        if (settingsStore.show3DScatterPlot){
            fetchFeaturess().then(()=>{
                updatePlotPoints();
            })
        }
    })
</script>

<template>
    <div id="main-filtervis">
        <div id="plot3dDiv" v-if="settingsStore.show3DScatterPlot">
            <Plot3d :data="plotPoints?plotPoints:[]" ref="plot3DRef"></Plot3d>
            <div id="loadingDiv" class="full" v-if="!dataObtained || !feats">
                <LoadingWidget v-if="featsRaw === null"></LoadingWidget>
                <p class="status" v-else>Data not ready</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
    div#main-filtervis{
        display: flex;
        width: 100%;
        height: 100%;
    }

    .full{
        width: 100%;
        height: 100%;
    }

    div#plot3dDiv{
        height: 430px;
        width: 100%;
        overflow: hidden;
        border-radius: 10px;
        z-index: 1;
        box-shadow: 0 0 5px var(--color-shadow);
    }
    div#loadingDiv{
        position:absolute;
        z-index: 2;
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