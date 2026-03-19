// ================= MOBILE MENU TOGGLE =================
const menuBtn = document.querySelector('.menu-btn');
const mobileMenu = document.querySelector('.mobile-menu');

if(menuBtn && mobileMenu){
  menuBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('active');
  });
}

// ================= ACTIVE NAV =================
document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(link=>{
  if(link.href === window.location.href){
    link.classList.add('active');
  }
});

// ================= MATRIX EFFECT =================
const box = document.querySelector('.matrix-box');
if(box){
  const canvas=document.createElement('canvas');
  box.appendChild(canvas);
  const ctx=canvas.getContext('2d');

  function resize(){
    canvas.width=box.clientWidth;
    canvas.height=box.clientHeight;
  }
  resize();
  window.addEventListener('resize',resize);

  const chars="01";
  const size=14;
  let cols=Math.floor(canvas.width/size);
  let drops=Array(cols).fill(0);

  function draw(){
    ctx.fillStyle="rgba(0,0,0,.15)";
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle="#19ffd2";
    ctx.font=size+"px monospace";

    drops.forEach((y,i)=>{
      const text=chars[Math.floor(Math.random()*2)];
      ctx.fillText(text,i*size,y*size);
      if(y*size>canvas.height && Math.random()>0.97) drops[i]=0;
      drops[i]++;
    });
    requestAnimationFrame(draw);
  }
  draw();
}
