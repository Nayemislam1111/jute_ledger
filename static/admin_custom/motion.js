document.addEventListener("DOMContentLoaded", function() {
    let canvas = document.createElement('canvas');
    canvas.id = 'motion-canvas';
    document.body.appendChild(canvas);

    let ctx = canvas.getContext('2d');
    let width, height;

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    let jutes = [];
    let juteSpacing = 12;
    let juteCount = Math.floor(width / juteSpacing) + 10;

    for (let i = 0; i < juteCount; i++) {
        jutes.push({
            x: i * juteSpacing + (Math.random() * 4 - 2),
            height: 35 + Math.random() * 20, // 👈 গাছের সাইজ আরও ছোট করা হয়েছে
            thickness: 1.8 + Math.random(),
            angle: Math.random() * Math.PI * 2,
            isCut: false,
            cutProgress: 0,
            leafColor: Math.random() > 0.3 ? '#2e7d32' : '#1b5e20',
            fiberColor: '#c0ca33'
        });
    }

    let cutterX = -100;
    let speed = 2.0;

    function animate() {
        requestAnimationFrame(animate);
        ctx.clearRect(0, 0, width, height);

        let groundLevel = height - 8; // 👈 মাটি স্ক্রিনের একদম নিচে নামানো হলো

        // ১. মাটির বর্ডার
        ctx.fillStyle = '#2d1e18';
        ctx.fillRect(0, groundLevel, width, height - groundLevel);

        // ২. ক্যাটানি/কাটার মোশন
        cutterX += speed;
        if (cutterX > width + 150) {
            cutterX = -100;
            jutes.forEach(j => { j.isCut = false; j.cutProgress = 0; });
        }

        // ৩. ছোট পাট গাছ আঁকা
        jutes.forEach(jute => {
            jute.angle += 0.025; 
            let sway = Math.sin(jute.angle) * 4;

            if (cutterX >= jute.x && !jute.isCut) {
                jute.isCut = true;
            }

            ctx.save();

            if (!jute.isCut) {
                let startX = jute.x;
                let startY = groundLevel;
                let tipX = jute.x + sway;
                let tipY = groundLevel - jute.height;

                ctx.strokeStyle = '#43a047';
                ctx.lineWidth = jute.thickness;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(startX, startY);
                ctx.quadraticCurveTo(jute.x + (sway * 0.5), groundLevel - (jute.height * 0.5), tipX, tipY);
                ctx.stroke();

                // সূক্ষ্ম পাতা
                let leafClusters = 3;
                for (let l = 1; l <= leafClusters; l++) {
                    let ratio = l / leafClusters;
                    let lx = startX + (tipX - startX) * ratio;
                    let ly = startY + (tipY - startY) * ratio;
                    
                    drawRealLeaf(ctx, lx, ly, -15 + sway * 0.3, ratio * 6, jute.leafColor);
                    drawRealLeaf(ctx, lx, ly, 15 + sway * 0.3, ratio * 6, jute.leafColor);
                }

                ctx.fillStyle = '#66bb6a';
                ctx.beginPath();
                ctx.ellipse(tipX, tipY, 4, 6, (sway * 0.05), 0, Math.PI * 2);
                ctx.fill();

            } else {
                if (jute.cutProgress < Math.PI / 2.1) {
                    jute.cutProgress += 0.08;
                }

                ctx.translate(jute.x, groundLevel);
                ctx.rotate(jute.cutProgress);

                ctx.strokeStyle = jute.fiberColor;
                ctx.lineWidth = jute.thickness;
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(0, -jute.height);
                ctx.stroke();

                ctx.restore();
                ctx.save();
                ctx.fillStyle = '#8d6e63';
                ctx.fillRect(jute.x - 1, groundLevel - 3, 2, 3);
            }

            ctx.restore();
        });

        // ৪. ব্লেড মোশন গ্লো
        let glowGradient = ctx.createRadialGradient(cutterX, groundLevel - 3, 0, cutterX, groundLevel - 3, 10);
        glowGradient.addColorStop(0, 'rgba(255, 235, 59, 0.9)');
        glowGradient.addColorStop(1, 'rgba(255, 235, 59, 0)');
        
        ctx.fillStyle = glowGradient;
        ctx.beginPath();
        ctx.arc(cutterX, groundLevel - 3, 10, 0, Math.PI * 2);
        ctx.fill();
    }

    function drawRealLeaf(ctx, x, y, angleDeg, size, color) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate((angleDeg * Math.PI) / 180);
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.quadraticCurveTo(size, -size / 2, size * 1.2, 0);
        ctx.quadraticCurveTo(size, size / 2, 0, 0);
        ctx.fill();
        ctx.restore();
    }

    animate();
});