var express = require('express');
var router = express.Router();
const {spawn} = require("child_process");
const max_workers = 2;
var sem = require('semaphore')(max_workers);

router.get('/info', function (req, res, next) {
    res.send(`tar ${process.env.TAR_PATH} and upload to ${process.env.UPLOAD_SCP_PATH}`)
});

router.get('/', function (req, res, next) {
    if (!sem.available()) {
        res.status(503).send("no available...");
    }
    var errmsg = ""
    sem.take(function () {
        const child = spawn("./archive-upload.sh", [process.env.TAR_PATH, process.env.UPLOAD_SCP_PATH, process.env.UPLOAD_SCP_PASS]);
        child.stdout.on("data", data => {
            console.log(`stdout: ${data}`);
        });
        child.stderr.on("data", data => {
            console.log(`stderr: ${data}`);
            errmsg = data
        });
        child.on('error', (error) => {
            sem.leave()
            console.log(`error: ${error.message}`);
            res.status(500).send(`[ERROR]: ${error.message}`);
        });
        child.on("close", code => {
            sem.leave()
            console.log(`child process exited with code ${code}`);
            if(code != 0) {
                res.status(500).send(`failed code:${code}/ msg: ${errmsg}`)
            }
            res.send(`success`);
        });
    })
});

module.exports = router;
