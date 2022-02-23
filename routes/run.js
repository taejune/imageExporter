var express = require('express');
var router = express.Router();
const { spawn } = require("child_process");

router.get('/info', function(req, res, next) {
  res.send("export volume " + process.env.DOCKER_REG_VOLUME_PATH + " to " + process.env.STATIC_SRV_VOLUME_PATH);
});

router.get('/', function(req, res, next) {
  const child = spawn("./exporter.sh", [process.env.DOCKER_REG_VOLUME_PATH, process.env.STATIC_SRV_VOLUME_PATH]);

  child.stdout.on("data", data => {
    console.log(`stdout: ${data}`);
  });

  child.stderr.on("data", data => {
    console.log(`stderr: ${data}`);
  });

  child.on('error', (error) => {
    console.log(`error: ${error.message}`);
    res.status(500).send(`[ERROR]: ${error.message}`);
  });

  child.on("close", code => {
    console.log(`child process exited with code ${code}`);
    res.send();
  });
});

module.exports = router;
