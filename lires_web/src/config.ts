
import { useSettingsStore } from "./components/store";

export function platformType(){
    if ((window as any).__TAURI__){
        return "tauri";
    }
    else{
        return "web";
    }
}

// get protocal from the current page
let FRONTEND_PROTOCAL: 'http:' | 'https:' = window.location.protocol as 'http:' | 'https:';

let FRONTENDURL: string;
FRONTENDURL = `${FRONTEND_PROTOCAL}//${window.location.hostname}:${window.location.port}`; //
if (import.meta.env.DEV){
    console.log("DEV mode");
}
else{
    // production code
    console.log("production mode")
}
function getBackendURL(){
    const BACKEND_PORT = useSettingsStore().backendPort;
    const BACKEND_HOST = useSettingsStore().backendHost;
    return `${BACKEND_HOST}:${BACKEND_PORT}`;
}

export {getBackendURL, FRONTENDURL};
export const MAINTAINER = {
    name: import.meta.env.VITE_MAINTAINER_NAME,
    email: import.meta.env.VITE_MAINTAINER_EMAIL
}

export const predefinedUsernames = [
    "SweetiePie", "CutiePatootie", "CuddleBug", "FluffyPaws", "HoneyBee",
    "SnuggleMuffin", "SugarPlum", "AngelFace", "PawsomePuppy", "TeddyBearHugs",
    "PrettyKitty", "LoveBug", "BabyDoll", "SunshineSmiles", "FuzzyWuzzy",
    "BumbleBee", "CupcakeQueen", "DoodleDaisy", "PurrfectPaws", "CuddlyKoala",
    "SweetPea", "BunnyHop", "SparklePony", "HappyPanda", "DreamyDove",
    "FluffyCloud", "CherryBlossom", "AngelicWhisper", "SnickerDoodle", "LuckyLadybug",
    "BlossomButterfly", "SugarCubes", "CottonCandyDreams", "HoneyBunches", "FurryFriend",
    "BabyBlueEyes", "SweetCheeks", "PawsitiveVibes", "SnugglyBear", "LovelyLlama",
    "PurrfectlyAdorable", "TwinkleToes", "CuddleBunny", "CookieCrumbs", "SunnySmiles",
    "FluffyKitten", "DarlingDeer", "ButterflyKisses", "FuzzyWuzzyPanda", "SweetDreamer",
    "SillyGoose", "DaisyDoodle", "CupcakeCutie", "BuzzyBee", "SnoozySnail",
    "CharmingChick", "CandyCane", "BerryBlossom", "Dimples", "CocoaCuddles",
    "CheerfulCherub", "PetalPaws", "BubblyBumble", "AngelWings", "JollyJellybean",
    "WhiskerWonder", "SprinkleSmiles", "GigglyGiraffe", "DancingDaisy", "SunnySideUp",
    "SnugglySloth", "CuteQuokka", "PeachyPaws", "BouncyBunny", "DazzlingDimples",
    "ChirpyChickadee", "CandyHeart", "CupcakeSprinkle", "BuzzyButterfly", "SnoozyPanda",
    "CharmingCorgi", "CottonCandyCloud", "BerryBlush", "DimpleDoll", "CocoaCuddler",
    "CheerfulChipmunk", "PetalWhiskers", "BubblyButterfly", "AngelFeathers", "JollyJumper",
    "WhiskerWanderer", "SprinkleSweets", "GigglyGazelle", "DancingDolphin", "SunnySmiles",
    "SnugglySquirrel", "CuteKangaroo", "PeachyPup", "BouncyBear", "DazzlingDarling",
    "ChirpyCockatiel", "CandyCharm", "CupcakeDelight", "BuzzyBee", "SnoozySloth",
    "CharmingChinchilla", "CottonCandyDream", "BerryBlossom", "DimpleDaisy", "CocoaCuddles",
    "CheerfulCheek", "PetalPurr", "BubblyBumblebee", "AngelWhispers", "JollyJester",
    "WhiskerWonder", "SprinkleSunshine", "GigglyGiraffe", "DancingDandelion", "SunnySideUp",
    "SnugglySheep", "CuteKoala", "PeachyPanda", "BouncyBunny", "DazzlingDaisy",
    "ChirpyChickadee", "CandyCane", "CupcakeCutie", "BuzzyButterfly", "SnoozySnail",
    "CharmingCherub", "CottonCandyCloud", "BerryBlush", "DimpleDoll", "CocoaCuddler",
    "CheerfulChipmunk", "PetalWhiskers", "BubblyButterfly", "AngelFeathers", "JollyJumper",
    "WhiskerWanderer", "SprinkleSweets", "GigglyGazelle", "DancingDolphin", "SunnySmiles",
    "SnugglySquirrel", "CuteKangaroo", "PeachyPup", "BouncyBear", "DazzlingDarling",
    "ChirpyCockatiel", "CandyCharm", "CupcakeDelight", "BuzzyBee", "SnoozySloth",
    "CharmingChinchilla", "CottonCandyDream", "BerryBlossom", "DimpleDaisy", "CocoaCuddles",
    "CheerfulCheek", "PetalPurr", "BubblyBumblebee", "AngelWhispers", "JollyJester",
    "WhiskerWonder", "SprinkleSunshine", "GigglyGiraffe", "DancingDandelion", "SunnySideUp",
    "SnugglySheep", "CuteKoala", "PeachyPanda", "BouncyBunny", "DazzlingDaisy",
  ];

