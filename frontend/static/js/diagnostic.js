if (!Auth.requireAuth()) throw 0;
const QUESTIONS=[
  {text:"C# dasturlash tili qaysi kompaniya tomonidan ishlab chiqilgan?",options:["Microsoft","Google","Oracle","Apple"],answer:0},
  {text:"C# da o'zgaruvchi e'lon qilishning to'g'ri usuli qaysi?",code:"// Qaysi variant to'g'ri?",options:["int x = 5;","x int = 5;","integer x = 5;","var = 5 int;"],answer:0},
  {text:"Quyidagi kod qanday natija beradi?",code:"int a = 10;\nint b = 3;\nConsole.WriteLine(a % b);",options:["3","1","0","3.33"],answer:1},
  {text:"C# da string birlashtirishning to'g'ri usuli qaysi?",options:["str1 + str2","str1 & str2","str1 . str2","str1 concat str2"],answer:0},
  {text:"'while' va 'do...while' tsikllarining asosiy farqi nima?",options:["do...while kamida bir marta bajariladi","while tezroq ishlaydi","do...while faqat sonlar uchun","farq yo'q"],answer:0},
  {text:"Massivni e'lon qilishning to'g'ri usuli qaysi?",code:"// C# da massiv e'lon qilish",options:["int[] arr = new int[5];","int arr[5];","array int arr = new[5];","int arr = array(5);"],answer:0},
  {text:"Quyidagi metodning qaytarish turi qanday?",code:"public static void Greet(string name) {\n  Console.WriteLine(\"Salom \" + name);\n}",options:["void — hech narsa qaytarmaydi","string","int","bool"],answer:0},
  {text:"OOP da 'encapsulation' tushunchasi nimani anglatadi?",options:["Ma'lumotlarni yashirish va himoya qilish","Meros olish","Ko'p shakllilik","Abstraksiya"],answer:0},
  {text:"C# da 'null' qiymati nima?",options:["Ob'ekt mavjud emasligi","0 soni","Bo'sh string","False qiymati"],answer:0},
  {text:"Quyidagi kod to'g'rimi?",code:"List<int> numbers = new List<int>();\nnumbers.Add(1);\nnumbers.Add(2);\nConsole.WriteLine(numbers.Count);",options:["Ha, 2 chiqaradi","Xato, List ishlatib bo'lmaydi","Xato, Count o'rniga Length","Ha, 0 chiqaradi"],answer:0},
  {text:"'break' operatori nima uchun ishlatiladi?",options:["Tsikldan chiqish uchun","O'zgaruvchi qiymatini o'chirish uchun","Metoddan chiqish uchun","Xatoni ushlash uchun"],answer:0},
  {text:"C# da 'interface' bilan 'abstract class' ning farqi?",options:["Interface faqat metod imzolarini o'z ichiga oladi","Interface realizatsiya qila oladi","Abstract class ko'p meros oladi","Farq yo'q"],answer:0},
  {text:"Quyidagi algoritmning vaqt murakkabligi qanday?",code:"for(int i = 0; i < n; i++) {\n  for(int j = 0; j < n; j++) {\n    // O(1) amal\n  }\n}",options:["O(n²)","O(n)","O(log n)","O(1)"],answer:0},
  {text:"'try-catch' bloki nima uchun ishlatiladi?",options:["Xatolarni ushlash va boshqarish uchun","Tsikl yaratish uchun","Metod chaqirish uchun","O'zgaruvchi e'lon qilish uchun"],answer:0},
  {text:"C# da 'static' kalit so'zi nimani anglatadi?",options:["Sinf nusxasisiz to'g'ridan-to'g'ri chaqiriladigan","O'zgarmas qiymat","Xususiy a'zo","Mavhum a'zo"],answer:0},
  {text:"Quyidagi kod qanday natija beradi?",code:"string s = \"Hello\";\nConsole.WriteLine(s.Length);",options:["5","6","4","Xato"],answer:0},
  {text:"Rekursiv funksiyada 'base case' nima?",options:["Rekursiyani to'xtatuvchi shart","Funksiyani chaqiruvchi qism","Parametrlar ro'yxati","Qaytarish turi"],answer:0},
  {text:"C# da 'LINQ' nima?",options:["Ma'lumotlar to'plamini so'rov qilish tili","Looplar uchun kutubxona","Xavfsizlik moduli","Tarmoq protokoli"],answer:0},
  {text:"Big O notatsiyasida quyidagilarning eng samarali tartiblash algoritmi qaysi?",options:["O(n log n) — Quick/Merge Sort","O(n²) — Bubble Sort","O(n) — Linear Sort","O(1) — Constant Sort"],answer:0},
  {text:"'async/await' C# da nima uchun ishlatiladi?",options:["Asinxron operatsiyalarni boshqarish","Xatolarni ushlash","Ma'lumotlar bazasiga ulanish","Fayllarni o'qish"],answer:0}
];

let current=0, score=0, selected=null, timerInterval=null, seconds=1200;
let userAnswers = {};

function startQuiz(){
  document.getElementById('introScreen').style.display='none';
  document.getElementById('quizScreen').style.display='block';
  startTimer();
  renderQ();
}

function startTimer(){
  timerInterval=setInterval(()=>{
    seconds--;
    const m=Math.floor(seconds/60).toString().padStart(2,'0');
    const s=(seconds%60).toString().padStart(2,'0');
    document.getElementById('timerTxt').textContent=`${m}:${s}`;
    if(seconds<=120) document.getElementById('timerEl').classList.add('warn');
    if(seconds<=0){clearInterval(timerInterval);showResult();}
  },1000);
}

function renderQ(){
  const q=QUESTIONS[current];
  document.getElementById('qNum').textContent='SAVOL '+String(current+1).padStart(2,'0');
  document.getElementById('qText').textContent=q.text;
  const codeEl=document.getElementById('qCode');
  if(q.code){codeEl.style.display='block';codeEl.textContent=q.code;}
  else codeEl.style.display='none';
  const opts=document.getElementById('optionsEl');
  opts.innerHTML=q.options.map((o,i)=>`
    <div class="option" onclick="pick(this,${i})">
      <div class="opt-letter">${'ABCD'[i]}</div>
      <span>${o}</span>
    </div>`).join('');
  document.getElementById('qLabel').textContent=`Savol ${current+1} / ${QUESTIONS.length}`;
  document.getElementById('qScore').textContent=`${score} ball`;
  document.getElementById('progFill').style.width=((current+1)/QUESTIONS.length*100)+'%';
  document.getElementById('nextBtn').disabled=true;
  selected=null;
}

function pick(el,i){
  if(selected!==null) return;
  selected=i;
  const q=QUESTIONS[current];
  document.querySelectorAll('.option').forEach((o,idx)=>{
    if(idx===q.answer) o.classList.add('correct');
    else if(idx===i&&i!==q.answer) o.classList.add('wrong');
    else if(idx===i) o.classList.add('selected');
  });
  userAnswers[String(current + 1)] = i;
  if(i===q.answer) score++;
  document.getElementById('nextBtn').disabled=false;
  document.getElementById('nextBtn').textContent=current===QUESTIONS.length-1?'Natijani ko\'rish ✓':'Keyingisi →';
}

function nextQ(){
  current++;
  if(current>=QUESTIONS.length){clearInterval(timerInterval);showResult();}
  else renderQ();
}

async function showResult(){
  document.getElementById('quizScreen').style.display='none';
  const rs=document.getElementById('resultScreen');
  rs.style.display='flex';
  const pct=Math.round(score/QUESTIONS.length*100);
  document.getElementById('rScore').textContent=score;
  document.getElementById('rCorrect').textContent=score;
  document.getElementById('rWrong').textContent=QUESTIONS.length-score;
  document.getElementById('rPct').textContent=pct+'%';
  let level,icon,title,desc,cls;
  if(pct<40){level='Beginner';icon='🌱';title='Yaxshi boshlash!';desc='Algoritmik fikrlash asoslarini o\'rganishga tayyormiz. Platforma sizga mos boshlang\'ich yo\'lni tavsiya qiladi.';cls='level-beginner';}
  else if(pct<70){level='Intermediate';icon='⚡';title='Yaxshi daraja!';desc='Siz asoslarni bilasiz. Platforma sizga o\'rta darajadan boshlab, qiyin mavzularni chuqurlashtiradi.';cls='level-intermediate';}
  else{level='Advanced';icon='🚀';title='Ajoyib!';desc='Siz yuqori darajada! Platforma sizga murakkab mavzular va algoritmik masalalarni tavsiya qiladi.';cls='level-advanced';}
  document.getElementById('rIcon').textContent=icon;
  document.getElementById('rLevel').textContent=level;
  document.getElementById('rLevel').className='result-level '+cls;
  document.getElementById('rTitle').textContent=title;
  document.getElementById('rDesc').textContent=desc;
  try { await api.post('/courses/diagnostic/', { answers: userAnswers }); } catch(e) {}
}
