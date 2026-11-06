const {chromium}=require('playwright');
const fs=require('fs');
const AxeBuilder=require('@axe-core/playwright').default;
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL?{channel:process.env.BROWSER_CHANNEL}:{})});
 const context=await browser.newContext();
 const page=await context.newPage(); const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 fs.mkdirSync('work/screenshots',{recursive:true});
 for(const width of [1440,375]){
  await page.setViewportSize({width,height:900});
  await page.goto('http://127.0.0.1:8765/');
  await page.evaluate(async()=>{await document.fonts.ready; await Promise.all(document.getAnimations().map(a=>a.finished));});
  const accessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  if(accessibility.violations.length)throw Error(JSON.stringify(accessibility.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
  await page.screenshot({path:`work/screenshots/library-${width}.png`,fullPage:false});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('horizontal overflow');
  if(await page.locator('.primer-card').count()!==27)throw Error('missing cards');
  if(await page.locator('.read-online').count()!==25)throw Error('missing readers');
  await page.locator('#searchInput').fill('solar');
  if(!await page.locator('#card-solar-energy').isVisible())throw Error('search failed');
  await page.locator('#searchInput').fill('');
  await page.locator('#filterBtn').click();
  for(const category of ['energy','infrastructure','materials','decarbonization','finance','technology','geopolitics','policy','agriculture']){
   await page.locator(`[data-cat="${category}"]`).click();
   if(!await page.locator('.primer-card:not(.hidden)').count())throw Error('empty category '+category);
   await page.locator(`[data-cat="${category}"]`).click();
  }
  await page.keyboard.press('Escape');
  if(await page.locator('#filterBtn').getAttribute('aria-expanded')!=='false')throw Error('escape failed');
  await page.locator('#sortBtn').click(); await page.locator('#sortBtn').click();
  await page.locator('.read-more-btn').first().click();
  if(await page.locator('.read-more-btn').first().getAttribute('aria-expanded')!=='true')throw Error('expand failed');
  await page.goto('http://127.0.0.1:8765/read/water-infrastructure.html');
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('reader overflow');
  if(!await page.locator('table').count()||!await page.locator('img').count())throw Error('reader lost media');
  await page.waitForFunction(()=>[...document.images].every(image=>image.complete&&image.naturalWidth>0));
  const readerAccessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  if(readerAccessibility.violations.length)throw Error(JSON.stringify(readerAccessibility.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
  await page.screenshot({path:`work/screenshots/reader-${width}.png`,fullPage:false});
 }
 await browser.close();
 if(errors.length)throw Error(errors.join('\n'));
 console.log('OK desktop/mobile, search, nine filters, sort, expansion, Escape, tables and images');
})().catch(e=>{console.error(e);process.exit(1)});
