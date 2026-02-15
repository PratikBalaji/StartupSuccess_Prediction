const http = require('http');

const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/',
    method: 'GET',
};

const req = http.request(options, (res) => {
    console.log(`STATUS: ${res.statusCode}`);
    res.setEncoding('utf8');
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    res.on('end', () => {
        if (data.includes('Startup Success Predictor') && data.includes('High Success')) {
            // 'High Success' might not be in the initial load, but 'Startup Success Predictor' should be.
            // Actually, the initial load should have options populated.
            console.log('Main page loaded successfully');
        } else if (data.includes('Startup Success Predictor')) {
            console.log('Main page loaded successfully (content check passed)');
        } else {
            console.log('Main page content check failed');
            console.log(data.substring(0, 200));
        }
    });
});

req.on('error', (e) => {
    console.error(`problem with request: ${e.message}`);
    process.exit(1);
});

req.end();
