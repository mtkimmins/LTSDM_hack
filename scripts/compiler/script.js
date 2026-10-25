//////////////////////////////////////////
//      CONSTANTS/VARS
//////////////////////////////////////////
//CONST
const topTaskbar = document.getElementById("top-taskbar");
const compileLTSDMButtom = document.getElementById("compile-ltsdm-button");
const compileSVGButtom = document.getElementById("compile-svg-button");
const compilePDFButtom = document.getElementById("compile-pdf-button");

const dataContainer = document.getElementById("data-container");

//VARS
let image_lock = false;







///////////////////////////////////////////
//      EVENT LISTENERS
///////////////////////////////////////////
function compileLTSDM(){};
function compileSVG(){};
function compilePDF(){};

function uploadAudio(){};
function resetAudio(){};

function playAudio(){};
function resumeAudio(){};
function stopAudio(){};

function selectLightInterval(){};
function moveLightIndicator(){};

function dragProgressBar(){};

function cutAudioSegment(){};
function jumpTime(){};
function assignLightColour(){};

function uploadImage(){};
function toggleImageEdits(){
    image_lock = !image_lock;
};

function compileFull() {};
function selectSaveFolder(){};


///////////////////////////////////////////
//      CREATION
///////////////////////////////////////////
function generateFrameElements() {};

function addFrameElements() {};

function initializeLTSDMElements() {};