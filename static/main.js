"use strict";
//exports.__esModule = true;

var drawingPad = document.getElementById('drawingPad');
var drawCtx = drawingPad.getContext('2d');
drawCtx.strokeStyle = 'lightblue'
var display = document.getElementById('display');
var displayCtx = display.getContext('2d');
var image
var image_id

function render_image(image_id) {
    image = new Image();
    image.onload = e => drawCtx.drawImage(image, 0, 0, drawingPad.width, drawingPad.height);
    image.src = '/images/' + image_id;
}

document.getElementById('bt:clear').onclick = (e) => { clear() }
document.getElementById('bt:fill').onclick = (e) => { fill() }
document.getElementById('bt:save').onclick = (e) => { save() }

function getCanvasXY(canvas, ev) {

    let x = ev.clientX - canvas.getBoundingClientRect().left
    x = x / canvas.scrollWidth
    x = Math.max(x, 0)
    x = Math.min(x, 1)
    x = x * canvas.width

    let y = ev.clientY - canvas.getBoundingClientRect().top
    y = y / canvas.scrollHeight
    y = Math.max(y, 0)
    y = Math.min(y, 1)
    y = y * canvas.height

    return {
        x: x,
        y: y,
    }
}

var inDrawpad = false;
drawingPad.onmouseenter = (e) => { inDrawpad = true; };
drawingPad.onmouseleave = (e) => { inDrawpad = false; };

var currX, currY, oldX, oldY;
var drawing = false;
var path = new Path2D();
var pathCollection = new Path2D();

function newPath() {
    pathCollection.addPath(path);
    path = new Path2D();
}

function updatePosition(x, y) {
    if (currX != undefined) oldX = currX;
    if (currY != undefined) oldY = currY;
    currX = x;
    currY = y;
}

function draw(ev) {
    let xy = getCanvasXY(drawingPad, ev);
    updatePosition(xy.x, xy.y)
    if (drawing) {
        path.lineTo(currX, currY);
        drawCtx.stroke(path);
        //displayCtx.stroke(path);
    }
}

function startDrawing(ev) {
    drawing = true;
    draw(ev);
}

function stopDrawing(ev) {
    if (!drawing) return;
    drawing = false;
    if (!inDrawpad) {
        path = new Path2D();
    }
}

function clearCanvas(ctx) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
}

function clear() {
    clearCanvas(drawCtx);
    drawCtx.drawImage(image, 0, 0, drawingPad.width, drawingPad.height);
    clearCanvas(displayCtx);
    console.debug('clear clicked')
    pathCollection = new Path2D();
}

function fill() {
    console.log('fill clicked');
    clearCanvas(drawCtx);
    drawCtx.drawImage(image, 0, 0, drawingPad.width, drawingPad.height);
    displayCtx.save();
    displayCtx.clip(path);
    displayCtx.drawImage(image, 0, 0, display.width, display.height);
    displayCtx.restore();
    newPath();
}

async function save() {
    const dataURL = renderROI();
    const resp = await post('/submit_roi', { 'id': image_id, 'roi': dataURL });
    const json = await resp.json();
    console.log(json)
}

async function initialize() {
    window.onmousedown = (e) => { console.log('mouse down') };
    //window.onmousemove = (e) => { console.log(getCanvasXY(drawingPad, e)) }
    window.onmousemove = draw;
    drawingPad.onmousedown = startDrawing;
    drawingPad.ontouchstart = startDrawing;
    window.onmouseup = stopDrawing;
    window.ontouchend = stopDrawing;
    document.getElementById('bt:next').onclick = next;
    document.getElementById('bt:back').onclick = back;
    document.getElementById('bt:finish').onclick = finish;
}

async function next(e) {
    console.log('next')
    location.href = '/next'
}

async function back(e) {
    console.log('back clicked.')
    location.href = '/back'
}

async function finish(e) {
    console.log('finish clicked')
    location.href = '/finish'
}

function renderROI() {
    clearCanvas(displayCtx);
    displayCtx.fill(pathCollection);
    pathCollection = new Path2D();
    return display.toDataURL();
}

async function post(url, data) {
    return fetch(
        url,
        {
            'method': 'post',
            'headers': { "Content-Type": "application/json; charset=utf-8" },
            'body': JSON.stringify(data)
        }
    )
}

function renderDisplay(data) {
    console.log(data)
    image_id = data.image_id
    render_image(data.image_id)
    initialize()
}