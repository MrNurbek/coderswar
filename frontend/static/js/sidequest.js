if (!Auth.requireAuth()) throw 0;

const _params  = new URLSearchParams(location.search);
const TOPIC_ID = parseInt(_params.get('topic')) || null;
const INIT_LVL = _params.get('level') || 'beginner';

const LEVEL_TASKS_DEMO = {
  beginner: [
    {n:1,name:"String uzunligini hisoblash",status:'done',score:8,diff:'easy',
     desc:"Foydalanuvchidan string kiriting va uning uzunligini ekranga chiqaring.",
     hint:`string s = Console.ReadLine();\nConsole.WriteLine(s.Length);`,
     examples:[{in:"Hello",out:"5"},{in:"Coders War",out:"10"}],
     methods:"string.Length — string uzunligini qaytaradi",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Uzunlikni hisoblang va chiqaring\n        \n    }\n}`,
     testCases:[{inp:"Hello",exp:"5",pass:true},{inp:"Coders War",exp:"10",pass:true},{inp:"",exp:"0",pass:true}]},
    {n:2,name:"Katta harfga o'tkazish",status:'done',score:8,diff:'easy',
     desc:"Kiritilgan stringni to'liq katta harflarga o'tkazib chiqaring.",
     hint:`Console.WriteLine(s.ToUpper());`,
     examples:[{in:"salom",out:"SALOM"},{in:"hello world",out:"HELLO WORLD"}],
     methods:"string.ToUpper() · string.ToLower()",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Katta harfga o'tkazib chiqaring\n        \n    }\n}`,
     testCases:[{inp:"salom",exp:"SALOM",pass:true},{inp:"hello",exp:"HELLO",pass:true},{inp:"cSharp",exp:"CSHARP",pass:true}]},
    {n:3,name:"Stringni teskari aylantirish",status:'done',score:8,diff:'easy',
     desc:"Berilgan stringni teskari tartibda chiqaring. Masalan: 'abc' → 'cba'",
     hint:`char[] arr = s.ToCharArray();\nArray.Reverse(arr);\nConsole.WriteLine(new string(arr));`,
     examples:[{in:"hello",out:"olleh"},{in:"12345",out:"54321"}],
     methods:"string.ToCharArray() · Array.Reverse() · new string(char[])",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Teskari aylantiring\n        \n    }\n}`,
     testCases:[{inp:"hello",exp:"olleh",pass:true},{inp:"abc",exp:"cba",pass:true},{inp:"racecar",exp:"racecar",pass:true}]},
    {n:4,name:"So'zlar sonini hisoblash",status:'done',score:8,diff:'easy',
     desc:"Kiritilgan jumlada nechta so'z borligini aniqlang.",
     hint:`string[] words = s.Split(' ');\nConsole.WriteLine(words.Length);`,
     examples:[{in:"Salom dunyo",out:"2"},{in:"Men C# o'rganaman",out:"4"}],
     methods:"string.Split(char) · array.Length",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // So'zlar sonini hisoblang\n        \n    }\n}`,
     testCases:[{inp:"Salom dunyo",exp:"2",pass:true},{inp:"a b c d",exp:"4",pass:true},{inp:"bitta",exp:"1",pass:true}]},
    {n:5,name:"String boshini tekshirish",status:'todo',score:null,diff:'easy',
     desc:"Kiritilgan string 'Hello' bilan boshlanadimi? true/false chiqaring.",
     hint:`Console.WriteLine(s.StartsWith("Hello"));`,
     examples:[{in:"Hello World",out:"true"},{in:"Goodbye",out:"false"}],
     methods:"string.StartsWith() · string.EndsWith()",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // StartsWith tekshiring\n        \n    }\n}`,
     testCases:[{inp:"Hello World",exp:"true",pass:null},{inp:"Goodbye",exp:"false",pass:null}]},
    {n:6,name:"Bo'shliqlarni tozalash",status:'todo',score:null,diff:'easy',
     desc:"Kiritilgan stringning bosh va oxiridagi bo'shliqlarni olib tashlang.",
     hint:`Console.WriteLine(s.Trim());`,
     examples:[{in:"  salom  ",out:"salom"},{in:" hello ",out:"hello"}],
     methods:"string.Trim() · string.TrimStart() · string.TrimEnd()",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Trim qiling\n        \n    }\n}`,
     testCases:[{inp:"  salom  ",exp:"salom",pass:null},{inp:" hello ",exp:"hello",pass:null}]},
    {n:7,name:"Qism string topish",status:'todo',score:null,diff:'easy',
     desc:"'csharp' so'zi kiritilgan string ichida bormi? Contains() yordamida tekshiring.",
     hint:`Console.WriteLine(s.ToLower().Contains("csharp"));`,
     examples:[{in:"I love csharp",out:"true"},{in:"Python is great",out:"false"}],
     methods:"string.Contains() · string.ToLower()",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Contains tekshiring\n        \n    }\n}`,
     testCases:[{inp:"I love csharp",exp:"true",pass:null},{inp:"Python is great",exp:"false",pass:null}]},
    {n:8,name:"String almashtirish",status:'todo',score:null,diff:'easy',
     desc:"Jumlada birinchi so'zni ikkinchi so'z bilan almashtiring (3 qator kiritish).",
     hint:`string result = sentence.Replace(oldWord, newWord);`,
     examples:[{in:"Salom dunyo\nSalom\nXayr",out:"Xayr dunyo"}],
     methods:"string.Replace(old, new)",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string sentence = Console.ReadLine();\n        string oldWord  = Console.ReadLine();\n        string newWord  = Console.ReadLine();\n        \n    }\n}`,
     testCases:[{inp:"Salom dunyo\nSalom\nXayr",exp:"Xayr dunyo",pass:null}]},
    {n:9,name:"Raqam stringmi?",status:'todo',score:null,diff:'easy',
     desc:"Kiritilgan string faqat raqamlardan iboratmi tekshiring.",
     hint:`bool isNum = s.All(char.IsDigit);`,
     examples:[{in:"12345",out:"true"},{in:"12a34",out:"false"}],
     methods:"LINQ: .All() · char.IsDigit()",
     template:`using System;\nusing System.Linq;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Faqat raqam ekanini tekshiring\n        \n    }\n}`,
     testCases:[{inp:"12345",exp:"true",pass:null},{inp:"12a34",exp:"false",pass:null}]},
    {n:10,name:"String birlashtirish",status:'todo',score:null,diff:'easy',
     desc:"N ta stringni kiritib, hammasini bitta qatorda birlashtiring (bo'sh joy bilan).",
     hint:`string[] lines = new string[n];\n// for loop bilan o'qing\nConsole.WriteLine(string.Join(" ", lines));`,
     examples:[{in:"3\nSalom\nDunyo\nC#",out:"Salom Dunyo C#"}],
     methods:"string.Join() · Console.ReadLine() · int.Parse()",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        string[] parts = new string[n];\n        for (int i = 0; i < n; i++) parts[i] = Console.ReadLine();\n        // Birlashtiring\n        \n    }\n}`,
     testCases:[{inp:"3\nSalom\nDunyo\nC#",exp:"Salom Dunyo C#",pass:null}]},
  ],
  beginner_project: {
    name:"Matn tahlilchisi",score:null,done:false,
    desc:"Matn tahlilchisi dastur yarating: foydalanuvchidan matn qabul qilib, so'zlar soni, harflar soni (bo'sh joysiz), eng uzun so'z va palindrom so'zlar ro'yxatini chiqaring.",
    hint:`string[] words = text.Split(' ');\n// So'zlar: words.Length\n// Harflar: text.Replace(" ", "").Length\n// Eng uzun: words.OrderByDescending(w => w.Length).First()`,
    examples:[{in:"racecar is a palindrome test",out:"So'zlar: 5\nHarflar: 28\nEng uzun: palindrome\nPalindromlar: racecar, a"}],
    template:`using System;\nusing System.Linq;\n\nclass MiniProject {\n    static void Main() {\n        string text = Console.ReadLine();\n        string[] words = text.Split(' ');\n        \n        // 1. So'zlar sonini chiqaring\n        \n        // 2. Harflar sonini chiqaring (bo'sh joysiz)\n        \n        // 3. Eng uzun so'zni toping\n        \n        // 4. Palindromlarni toping va chiqaring\n        \n    }\n}`,
    testCases:[{inp:"racecar is a test",exp:"So'zlar: 4",pass:null}],
  },

  intermediate: [
    {n:1,name:"Palindrom tekshirish",status:'todo',score:null,diff:'medium',
     desc:"Kiritilgan so'z palindrommi yoki yo'qligini aniqlang.",
     hint:`bool isPalin = s == new string(s.ToCharArray().Reverse().ToArray());`,
     examples:[{in:"racecar",out:"true"},{in:"hello",out:"false"}],
     methods:"LINQ: .Reverse().ToArray() · string comparison",
     template:`using System;\nusing System.Linq;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Palindrom tekshiring\n        \n    }\n}`,
     testCases:[{inp:"racecar",exp:"true",pass:null},{inp:"hello",exp:"false",pass:null}]},
    {n:2,name:"Email tekshirish",status:'todo',score:null,diff:'medium',
     desc:"Kiritilgan email manzili to'g'ri formatdami yoki yo'qligini aniqlang.",
     hint:`bool valid = email.Contains("@") && email.IndexOf('.') > email.IndexOf('@');`,
     examples:[{in:"user@email.com",out:"valid"},{in:"notanemail",out:"invalid"}],
     methods:"string.Contains() · string.IndexOf()",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string email = Console.ReadLine();\n        // Email to'g'riligini tekshiring\n        \n    }\n}`,
     testCases:[{inp:"user@email.com",exp:"valid",pass:null},{inp:"bad",exp:"invalid",pass:null}]},
    {n:3,name:"Eng uzun so'zni topish",status:'todo',score:null,diff:'medium',
     desc:"Kiritilgan jumladan eng uzun so'zni toping.",
     hint:`string longest = words.OrderByDescending(w => w.Length).First();`,
     examples:[{in:"Men dasturlashni yaxshi ko'raman",out:"dasturlashni"}],
     methods:"LINQ: OrderByDescending · .First()",
     template:`using System;\nusing System.Linq;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Eng uzun so'zni toping\n        \n    }\n}`,
     testCases:[{inp:"Men dasturlashni sevaman",exp:"dasturlashni",pass:null}]},
    {n:4,name:"Harflar chastotasi",status:'todo',score:null,diff:'medium',
     desc:"Kiritilgan stringdagi har bir harfning necha marta uchrashini chiqaring.",
     hint:`var freq = s.ToLower().Where(char.IsLetter).GroupBy(c=>c).OrderBy(g=>g.Key);`,
     examples:[{in:"hello",out:"e:1\nh:1\nl:2\no:1"}],
     methods:"LINQ: GroupBy · OrderBy · Where · char.IsLetter",
     template:`using System;\nusing System.Linq;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // Harflar chastotasini chiqaring\n        \n    }\n}`,
     testCases:[{inp:"hello",exp:"e:1\nh:1\nl:2\no:1",pass:null}]},
    {n:5,name:"Caesar shifri",status:'todo',score:null,diff:'medium',
     desc:"Caesar shifri: har bir harfni N pozitsiyaga siljiting.",
     hint:`char shifted = (char)(((c - 'a' + n) % 26) + 'a');`,
     examples:[{in:"abc\n3",out:"def"},{in:"xyz\n3",out:"abc"}],
     methods:"char arithmetic · modulo % 26",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine().ToLower();\n        int n   = int.Parse(Console.ReadLine());\n        // Harflarni shifrlang\n        \n    }\n}`,
     testCases:[{inp:"abc\n3",exp:"def",pass:null},{inp:"xyz\n3",exp:"abc",pass:null}]},
    {n:6,name:"Anagram tekshirish",status:'todo',score:null,diff:'medium',
     desc:"Ikki so'z anagrammami tekshiring.",
     hint:`string sorted1 = new string(s1.OrderBy(c=>c).ToArray());`,
     examples:[{in:"listen\nsilent",out:"true"},{in:"hello\nworld",out:"false"}],
     methods:"LINQ: OrderBy · string comparison",
     template:`using System;\nusing System.Linq;\n\nclass Solution {\n    static void Main() {\n        string s1 = Console.ReadLine().ToLower();\n        string s2 = Console.ReadLine().ToLower();\n        // Anagram tekshiring\n        \n    }\n}`,
     testCases:[{inp:"listen\nsilent",exp:"true",pass:null},{inp:"hello\nworld",exp:"false",pass:null}]},
    {n:7,name:"So'zlarni teskari tartiblash",status:'todo',score:null,diff:'medium',
     desc:"Jumlaning so'zlarini teskari tartibda chiqaring.",
     hint:`string result = string.Join(" ", words.Reverse());`,
     examples:[{in:"Salom aziz dunyo",out:"dunyo aziz Salom"}],
     methods:"LINQ: .Reverse() · string.Join()",
     template:`using System;\nusing System.Linq;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine();\n        // So'zlarni teskari tartibga keltiring\n        \n    }\n}`,
     testCases:[{inp:"Salom aziz dunyo",exp:"dunyo aziz Salom",pass:null}]},
    {n:8,name:"Takrorlanuvchi harfni topish",status:'todo',score:null,diff:'medium',
     desc:"Stringdagi birinchi takrorlanuvchi harfni toping.",
     hint:`var seen = new HashSet<char>();\nforeach (char c in s.ToLower()) { if (!seen.Add(c)) { Console.WriteLine(c); break; } }`,
     examples:[{in:"abcabc",out:"a"},{in:"programming",out:"r"}],
     methods:"HashSet<char> · foreach · char comparison",
     template:`using System;\nusing System.Collections.Generic;\n\nclass Solution {\n    static void Main() {\n        string s = Console.ReadLine().ToLower();\n        // Birinchi takrorlanuvchi harfni toping\n        \n    }\n}`,
     testCases:[{inp:"abcabc",exp:"a",pass:null},{inp:"programming",exp:"r",pass:null}]},
    {n:9,name:"Regex bilan validatsiya",status:'todo',score:null,diff:'hard',
     desc:"Regex yordamida telefon raqamini tekshiring: +998XXXXXXXXX formati.",
     hint:`bool valid = Regex.IsMatch(phone, @"^\\+998\\d{9}$");`,
     examples:[{in:"+998901234567",out:"valid"},{in:"998901234567",out:"invalid"}],
     methods:"System.Text.RegularExpressions.Regex.IsMatch()",
     template:`using System;\nusing System.Text.RegularExpressions;\n\nclass Solution {\n    static void Main() {\n        string phone = Console.ReadLine();\n        // Regex bilan tekshiring\n        \n    }\n}`,
     testCases:[{inp:"+998901234567",exp:"valid",pass:null},{inp:"998901234567",exp:"invalid",pass:null}]},
    {n:10,name:"StringBuilder bilan ishlash",status:'todo',score:null,diff:'hard',
     desc:"StringBuilder yordamida 1 dan N gacha sonlarni vergul bilan birlashtiring.",
     hint:`var sb = new StringBuilder();\nfor (int i = 1; i <= n; i++) { sb.Append(i); if (i < n) sb.Append(","); }`,
     examples:[{in:"5",out:"1,2,3,4,5"},{in:"3",out:"1,2,3"}],
     methods:"StringBuilder.Append() · StringBuilder.ToString()",
     template:`using System;\nusing System.Text;\n\nclass Solution {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        // StringBuilder bilan birlashtiring\n        \n    }\n}`,
     testCases:[{inp:"5",exp:"1,2,3,4,5",pass:null},{inp:"3",exp:"1,2,3",pass:null}]},
  ],
  intermediate_project: {
    name:"Parol kuchi tekshirgich",score:null,done:false,
    desc:"Parol kuchini tekshiruvchi dastur yarating. Parol kuchi:\n- Kamida 8 belgi\n- Katta va kichik harf\n- Raqam\n- Maxsus belgi (@, !, #, $, %)\n\nChiqarish: 'Kuchsiz', 'O'rtacha', 'Kuchli'",
    hint:`bool hasUpper = password.Any(char.IsUpper);\nbool hasDigit = password.Any(char.IsDigit);\nbool hasSpecial = "@!#$%".Any(c => password.Contains(c));`,
    examples:[{in:"abc",out:"Kuchsiz"},{in:"Pass123",out:"O'rtacha"},{in:"Pass123!@",out:"Kuchli"}],
    template:`using System;\nusing System.Linq;\n\nclass PasswordChecker {\n    static void Main() {\n        string password = Console.ReadLine();\n        bool longEnough = password.Length >= 8;\n        // Natijani chiqaring\n        \n    }\n}`,
    testCases:[{inp:"abc",exp:"Kuchsiz",pass:null},{inp:"Pass123",exp:"O'rtacha",pass:null}],
  },

  advanced: [
    {n:1,name:"LINQ GroupBy — yosh guruhlash",status:'todo',score:null,diff:'hard',
     desc:"N ta kishini ism:yosh formatida kiritib, 18 dan katta va kichikka ajrating.",
     hint:`var groups = people.GroupBy(p => p.age >= 18 ? "Adult" : "Minor");`,
     examples:[{in:"3\nAli:20\nBob:15\nZina:22",out:"Adult: Ali, Zina\nMinor: Bob"}],
     methods:"LINQ: GroupBy · Select · string.Split(':')",
     template:`using System;\nusing System.Linq;\n\nclass Solution {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var people = Enumerable.Range(0,n).Select(_=>{\n            var p=Console.ReadLine().Split(':');\n            return (name:p[0], age:int.Parse(p[1]));\n        }).ToList();\n        // GroupBy bilan guruhlang\n        \n    }\n}`,
     testCases:[{inp:"3\nAli:20\nBob:15\nZina:22",exp:"Adult: Ali, Zina",pass:null}]},
    {n:2,name:"Delegate va event",status:'todo',score:null,diff:'hard',
     desc:"Hisoblash delegatini yarating: ikkita int → int.",
     hint:`Func<int,int,int> add = (a,b) => a+b;`,
     examples:[{in:"10\n3",out:"+:13\n-:7\n*:30\n/:3"}],
     methods:"Func<T,T,T> · Lambda expressions",
     template:`using System;\nusing System.Collections.Generic;\n\nclass Solution {\n    static void Main() {\n        int a = int.Parse(Console.ReadLine());\n        int b = int.Parse(Console.ReadLine());\n        // Delegate'lardan foydalaning\n        \n    }\n}`,
     testCases:[{inp:"10\n3",exp:"+:13\n-:7\n*:30\n/:3",pass:null}]},
    {n:3,name:"Generic Stack implementatsiya",status:'todo',score:null,diff:'hard',
     desc:"Generic Stack<T> sinfini yarating: Push, Pop, Peek, IsEmpty metodlari bilan.",
     hint:`class MyStack<T> {\n    private List<T> _items = new();\n    public void Push(T item) => _items.Add(item);\n}`,
     examples:[{in:"push 1\npush 2\npop\npeek",out:"Popped: 2\nPeek: 1"}],
     methods:"Generic class · List<T> · Exception handling",
     template:`using System;\nusing System.Collections.Generic;\n\nclass MyStack<T> {\n    // Stack sinfini implement qiling\n}\n\nclass Program {\n    static void Main() {\n        var stack = new MyStack<int>();\n        string line;\n        while ((line = Console.ReadLine()) != null) {\n            // Buyruqlarni bajarng\n        }\n    }\n}`,
     testCases:[{inp:"push 5\npush 3\npop\npeek",exp:"Popped: 3\nPeek: 5",pass:null}]},
    {n:4,name:"async/await — parallel download",status:'todo',score:null,diff:'hard',
     desc:"3 ta URL uchun 'yuklash' simulatsiya qiling. Task.WhenAll() ishlatib parallel bajaring.",
     hint:`var tasks = urls.Select(async url => { await Task.Delay(1000); return $"{url}: OK"; });\nvar results = await Task.WhenAll(tasks);`,
     examples:[{in:"3\nhttps://a.com\nhttps://b.com\nhttps://c.com",out:"3 ta URL yuklandi"}],
     methods:"async/await · Task.WhenAll() · Task.Delay()",
     template:`using System;\nusing System.Linq;\nusing System.Threading.Tasks;\n\nclass Solution {\n    static async Task Main() {\n        int n = int.Parse(Console.ReadLine());\n        var urls = Enumerable.Range(0,n).Select(_=>Console.ReadLine()).ToArray();\n        // Parallel yuklang\n        \n    }\n}`,
     testCases:[{inp:"3\na\nb\nc",exp:"3 ta URL yuklandi",pass:null}]},
    {n:5,name:"Expression tree",status:'todo',score:null,diff:'hard',
     desc:"Lambda dan expression tree yarating va Compile() qilib chaqiring.",
     hint:`Expression<Func<int,bool>> expr = x => x > 5;\nvar compiled = expr.Compile();`,
     examples:[{in:"7",out:"true"},{in:"3",out:"false"}],
     methods:"Expression<Func<T,TResult>> · Compile() · Lambda",
     template:`using System;\nusing System.Linq.Expressions;\n\nclass Solution {\n    static void Main() {\n        int x = int.Parse(Console.ReadLine());\n        // Expression tree yarating: x > 5\n        \n    }\n}`,
     testCases:[{inp:"7",exp:"true",pass:null},{inp:"3",exp:"false",pass:null}]},
    {n:6,name:"IDisposable va using",status:'todo',score:null,diff:'hard',
     desc:"IDisposable implement qiluvchi Resource sinfini yarating.",
     hint:`class Resource : IDisposable {\n    public void Dispose() { Console.WriteLine("Resurs ozod qilindi"); }\n}`,
     examples:[{in:"start",out:"Resurs yaratildi\nResurs ishlamoqda\nResurs ozod qilindi"}],
     methods:"IDisposable · using statement · GC.SuppressFinalize()",
     template:`using System;\n\nclass Resource : IDisposable {\n    // IDisposable implement qiling\n}\n\nclass Program {\n    static void Main() {\n        string cmd = Console.ReadLine();\n        // using bilan ishlatish\n        \n    }\n}`,
     testCases:[{inp:"start",exp:"Resurs ozod qilindi",pass:null}]},
    {n:7,name:"Covariance bilan collection",status:'todo',score:null,diff:'hard',
     desc:"IEnumerable<T> covariance ishlatib, Animal ro'yxatidan Dog ro'yxatini qabul qiluvchi metod yozing.",
     hint:`void PrintAnimals(IEnumerable<Animal> animals) {...}`,
     examples:[{in:"3\nRex\nBuddy\nMax",out:"Rex\nBuddy\nMax"}],
     methods:"IEnumerable<out T> covariance · Polymorphism",
     template:`using System;\nusing System.Collections.Generic;\n\nclass Animal { public string Name {get;set;} public Animal(string n){Name=n;} }\nclass Dog : Animal { public Dog(string n):base(n){} }\n\nclass Solution {\n    static void PrintAnimals(IEnumerable<Animal> animals) {\n        foreach(var a in animals) Console.WriteLine(a.Name);\n    }\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        // Dog ro'yxati yarating va PrintAnimals ga bering\n        \n    }\n}`,
     testCases:[{inp:"3\nRex\nBuddy\nMax",exp:"Rex\nBuddy\nMax",pass:null}]},
    {n:8,name:"Reflection bilan xususiyat o'qish",status:'todo',score:null,diff:'hard',
     desc:"Reflection orqali ob'ektning barcha public xususiyatlarini nom:qiymat formatida chiqaring.",
     hint:`var props = obj.GetType().GetProperties();\nforeach(var p in props) Console.WriteLine($"{p.Name}:{p.GetValue(obj)}");`,
     examples:[{in:"Ali\n25",out:"Name:Ali\nAge:25"}],
     methods:"Type.GetProperties() · PropertyInfo.GetValue() · typeof()",
     template:`using System;\nusing System.Reflection;\n\nclass Person { public string Name{get;set;} public int Age{get;set;} }\n\nclass Solution {\n    static void Main() {\n        string name = Console.ReadLine();\n        int age = int.Parse(Console.ReadLine());\n        var person = new Person { Name=name, Age=age };\n        // Reflection bilan chiqaring\n        \n    }\n}`,
     testCases:[{inp:"Ali\n25",exp:"Name:Ali\nAge:25",pass:null}]},
    {n:9,name:"Source Generator pattern",status:'todo',score:null,diff:'hard',
     desc:"Berilgan xususiyatlar ro'yxati uchun getter/setter kodi generatsiya qiluvchi dastur yozing.",
     hint:`string GenProp(string name, string type) =>\n    $"public {type} {name} {{ get; set; }}";`,
     examples:[{in:"2\nName:string\nAge:int",out:"public string Name { get; set; }\npublic int Age { get; set; }"}],
     methods:"string interpolation · Split · template generation",
     template:`using System;\n\nclass CodeGen {\n    static string GenProp(string name, string type) {\n        return "";\n    }\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        for(int i=0;i<n;i++) {\n            var parts = Console.ReadLine().Split(':');\n            Console.WriteLine(GenProp(parts[0], parts[1]));\n        }\n    }\n}`,
     testCases:[{inp:"2\nName:string\nAge:int",exp:"public string Name { get; set; }",pass:null}]},
    {n:10,name:"Memory<T> vs Span<T>",status:'todo',score:null,diff:'hard',
     desc:"int[] massivning o'rta qismini Span<int> orqali sum hisoblang.",
     hint:`var span = arr.AsSpan(start, length);\nint sum = 0;\nforeach(int x in span) sum += x;`,
     examples:[{in:"5\n1 2 3 4 5\n1\n3",out:"9"}],
     methods:"AsSpan(start, length) · Span<T> · foreach",
     template:`using System;\n\nclass Solution {\n    static void Main() {\n        int n = int.Parse(Console.ReadLine());\n        var arr = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);\n        int start  = int.Parse(Console.ReadLine());\n        int length = int.Parse(Console.ReadLine());\n        // Span<int> bilan hisoblang\n        \n    }\n}`,
     testCases:[{inp:"5\n1 2 3 4 5\n1\n3",exp:"9",pass:null}]},
  ],
  advanced_project: {
    name:"Mini ORM yaratish",score:null,done:false,
    desc:"Minimal ORM yarating:\n- [Table], [Column] attributlari\n- Reflection orqali CREATE TABLE SQL generatsiya\n- INSERT INTO SQL generatsiya",
    hint:`var props = typeof(T).GetProperties()\n    .Where(p => p.GetCustomAttribute<ColumnAttr>() != null);`,
    examples:[{in:"User\nId:int\nName:string",out:"CREATE TABLE User (Id INT, Name VARCHAR(255));"}],
    template:`using System;\nusing System.Linq;\nusing System.Reflection;\n\n[AttributeUsage(AttributeTargets.Class)] class TableAttr : Attribute { public string Name; public TableAttr(string n){Name=n;} }\n[AttributeUsage(AttributeTargets.Property)] class ColumnAttr : Attribute {}\n\nclass MiniORM {\n    static void Main() {\n        // ...\n    }\n}`,
    testCases:[{inp:"User\nId:int\nName:string",exp:"CREATE TABLE User",pass:null}],
  },
};

const LEVEL_LOCKS = { beginner: false, intermediate: true, advanced: true };
let curLevel  = 'beginner';
let curIdx    = 0;
let isProject = false;

let API_TASKS = {};

function getCurTasks()   { const s = Object.keys(API_TASKS).length ? API_TASKS : LEVEL_TASKS_DEMO; return s[curLevel] || []; }
function getCurProject() { const s = Object.keys(API_TASKS).length ? API_TASKS : LEVEL_TASKS_DEMO; return s[`${curLevel}_project`]; }

function switchLevel(level) {
  if (LEVEL_LOCKS[level]) {
    showToast('🔒 Bu daraja qulflanmagan! Avvalgi darajani tugatng.');
    return;
  }
  curLevel = level;
  curIdx   = 0;
  isProject = false;

  const map = {beginner:'lb', intermediate:'lo', advanced:'ly'};
  const actMap = {beginner:'active-lb', intermediate:'active-lo', advanced:'active-ly'};
  const nameMap = {beginner:"Boshlang'ich", intermediate:"O'rta", advanced:'Yuqori'};
  const badgeCls = {beginner:'b', intermediate:'o', advanced:'y'};

  ['beginner','intermediate','advanced'].forEach(lv => {
    const btn = document.getElementById(`lvTab${lv[0].toUpperCase()}`);
    btn.className = `lv-tab ${map[lv]}`;
    if (lv === level) btn.classList.add(actMap[lv]);
  });

  const badge = document.getElementById('lvBadge');
  badge.textContent = nameMap[level];
  badge.className = `lv-badge ${badgeCls[level]}`;

  const proj = getCurProject();
  if (proj) {
    document.getElementById('projectName').textContent = proj.name;
    document.getElementById('projectItem').className = 'mini-proj' + (proj.done ? ' done' : '');
  }

  renderTaskList();
  loadTask(0);
}

function renderTaskList(){
  const tasks = getCurTasks();
  const done  = tasks.filter(t=>t.status==='done').length;
  const total = tasks.length;
  const ball  = tasks.filter(t=>t.status==='done').reduce((a,t)=>a+(t.score||0),0);

  document.getElementById('tpProgLabel').textContent = `${done} / ${total} topshiriq`;
  document.getElementById('tpBall').textContent = `+${ball} ball`;
  document.getElementById('taskBar').style.width = (done/total*100)+'%';

  document.getElementById('taskListEl').innerHTML=tasks.map((t,i)=>`
    <div class="task-item ${!isProject&&i===curIdx?'active':''} ${t.status==='done'?'done':''}" onclick="loadTask(${i})">
      <div class="ti-row">
        <div class="ti-num ${t.status==='done'?'tn-done':!isProject&&i===curIdx?'tn-active':'tn-todo'}">${t.status==='done'?'✓':t.n}</div>
        <div class="ti-info">
          <div class="ti-name">${t.name}</div>
          <span class="ti-diff ${t.diff==='easy'?'d-easy':t.diff==='medium'?'d-med':'d-hard'}">${t.diff==='easy'?'Oson':t.diff==='medium'?"O'rta":'Qiyin'}</span>
        </div>
        ${t.score?`<div class="ti-score" style="color:#43e97b">+${t.score}</div>`:''}
      </div>
    </div>`).join('');
}

function loadTask(i){
  curIdx=i;
  isProject=false;
  const t=getCurTasks()[i];
  if(!t) return;
  document.getElementById('curTaskNum').textContent=t.n;
  document.getElementById('curTaskName').textContent=t.name;
  document.getElementById('tdText').textContent=t.desc;
  document.getElementById('tdHint').textContent=t.hint;
  document.getElementById('tdMethods').innerHTML=t.methods;
  document.getElementById('tdExamples').innerHTML=t.examples.map(e=>`
    <div class="td-example">
      <div class="ex-label">Misol</div>
      <div class="ex-io">📥 Kiritish: <strong>${e.in.replace(/\n/g,' | ')}</strong></div>
      <div class="ex-io">📤 Chiqarish: <strong>${e.out}</strong></div>
    </div>`).join('');
  document.getElementById('codeArea').value=t.template||'';
  updateLines();
  clearOutput();
  hideBanner();
  renderTestCases();
  renderTaskList();
  switchView('desc');
}

function loadProject(){
  isProject=true;
  const p=getCurProject();
  if(!p) return;
  document.getElementById('curTaskNum').textContent='Loyiha';
  document.getElementById('curTaskName').textContent=p.name;
  document.getElementById('tdText').textContent=p.desc;
  document.getElementById('tdHint').textContent=p.hint||'';
  document.getElementById('tdMethods').innerHTML=p.methods||'';
  document.getElementById('tdExamples').innerHTML=(p.examples||[]).map(e=>`
    <div class="td-example">
      <div class="ex-label">Misol</div>
      <div class="ex-io">📥 Kiritish: <strong>${e.in.replace(/\n/g,' | ')}</strong></div>
      <div class="ex-io">📤 Chiqarish: <strong>${e.out.replace(/\n/g,' | ')}</strong></div>
    </div>`).join('');
  document.getElementById('codeArea').value=p.template||'';
  updateLines(); clearOutput(); hideBanner();
  document.getElementById('testContent').innerHTML=(p.testCases||[]).map((tc,i)=>`
    <div class="tc-row tc-pending"><div class="tc-icon">⏳</div>
    <div class="tc-info"><div class="tc-label">Test ${i+1}</div>
    <div class="tc-detail">${tc.inp.replace(/\n/g,' | ')} → ${tc.exp}</div></div></div>`).join('');
  renderTaskList();
  switchView('desc');
}

function switchView(v){
  const desc=document.getElementById('descPane');
  const editor=document.getElementById('editorPane');
  const btnD=document.getElementById('btnDesc');
  const btnC=document.getElementById('btnCode');
  if(v==='desc'){
    desc.classList.add('show'); editor.classList.add('hide');
    btnD.style.borderColor='var(--accent)'; btnD.style.color='#a78bfa';
    btnC.style.borderColor='var(--border)'; btnC.style.color='var(--text)';
  } else {
    desc.classList.remove('show'); editor.classList.remove('hide');
    btnC.style.borderColor='var(--accent)'; btnC.style.color='#a78bfa';
    btnD.style.borderColor='var(--border)'; btnD.style.color='var(--text)';
  }
}

function switchTab(t){
  ['out','tests','ai'].forEach(id=>{
    document.getElementById('tab-'+id).classList.remove('active');
  });
  document.getElementById('tab-'+t).classList.add('active');
  document.getElementById('outPanel').style.display=t==='out'?'flex':'none';
  document.getElementById('testsPanel').style.display=t==='tests'?'flex':'none';
  document.getElementById('aiFeedback').classList.toggle('show',t==='ai');
}

function updateLines(){
  const ta=document.getElementById('codeArea');
  const lines=ta.value.split('\n');
  document.getElementById('lineNums').innerHTML=lines.map((_,i)=>`<div class="ln">${i+1}</div>`).join('');
  document.getElementById('lineCount').textContent=lines.length;
}

function handleTab(e){
  if(e.key==='Tab'){e.preventDefault();const ta=e.target;const s=ta.selectionStart;ta.value=ta.value.substring(0,s)+'    '+ta.value.substring(ta.selectionEnd);ta.selectionStart=ta.selectionEnd=s+4;updateLines();}
}

function runCode(){
  setStatus('run','Ishga tushirilmoqda...');
  switchView('code'); switchTab('out');
  const out=document.getElementById('outputContent');
  out.innerHTML='<div class="out-line out-info">▶ Kodni bajarilmoqda (C# · .NET 8)...</div>';
  setTimeout(()=>{
    const t=isProject ? getCurProject() : getCurTasks()[curIdx];
    if(!t){setStatus('ready','Tayyor');return;}
    const ex=t.examples[0];
    out.innerHTML=`
      <div class="out-line out-info">✅ Kompilyatsiya muvaffaqiyatli</div>
      <div class="out-line out-info">📥 Test kiritish: "${ex.in.replace(/\n/g,' | ')}"</div>
      <div class="out-line" style="height:1px;background:rgba(255,255,255,0.06);margin:.3rem 0"></div>
      <div class="out-line out-success">${ex.out}</div>
      <div class="out-line" style="height:1px;background:rgba(255,255,255,0.06);margin:.3rem 0"></div>
      <div class="out-line out-info">⏱️ Vaqt: ${Math.floor(Math.random()*50+20)}ms · Xotira: ${Math.floor(Math.random()*8+12)}MB</div>`;
    setStatus('ready','Tayyor');
  },1200);
}

let _pollTimer = null;

async function submitCode() {
  const code = document.getElementById('codeArea').value.trim();
  if (!code) { showToast('❗ Avval kod yozing!'); return; }
  const t = isProject ? getCurProject() : getCurTasks()[curIdx];
  if (!t) return;

  setStatus('run', 'Tekshirilmoqda...');
  switchView('code');
  switchTab('tests');

  const tcs = t.testCases || [];
  document.getElementById('testContent').innerHTML = tcs.length
    ? tcs.map((tc, i) => `
        <div class="tc-row tc-pending" id="tc${i}">
          <div class="tc-icon">⏳</div>
          <div class="tc-info"><div class="tc-label">Test case ${i+1}</div>
            <div class="tc-detail">Kiritish: "${String(tc.inp||'').replace(/\n/g,' | ')}" · Kutilgan: "${tc.exp}"</div></div>
          <div class="tc-time">—</div>
        </div>`).join('')
    : '<div class="tc-row tc-pending"><div class="tc-icon">⏳</div><div class="tc-info"><div class="tc-label">Baholanmoqda...</div></div></div>';

  try {
    if (!t.id) { _simulateSubmit(t); return; }
    const res = await api.submitCode({ task: t.id, code, language: 'csharp' });
    _pollSubmission(res.id, t);
  } catch (err) {
    setStatus('ready', 'Tayyor');
    showBanner(false, '❌ Yuborishda xato: ' + (err.message || 'Server xatosi'), '');
  }
}

function _pollSubmission(subId, t) {
  if (_pollTimer) clearInterval(_pollTimer);
  let attempts = 0;
  _pollTimer = setInterval(async () => {
    attempts++;
    if (attempts > 30) {
      clearInterval(_pollTimer);
      setStatus('ready', 'Tayyor');
      showBanner(false, '❌ Vaqt tugadi — server javob bermadi', '');
      return;
    }
    try {
      const sub = await api.submission(subId);
      if (sub.status === 'pending' || sub.status === 'running') return;
      clearInterval(_pollTimer);
      setStatus('ready', 'Tayyor');

      const results = sub.test_results || [];
      results.forEach((r, i) => {
        const row = document.getElementById('tc' + i);
        if (!row) return;
        row.className = 'tc-row ' + (r.passed ? 'tc-pass' : 'tc-fail');
        row.querySelector('.tc-icon').textContent = r.passed ? '✅' : '❌';
        row.querySelector('.tc-label').textContent = r.passed
          ? `Test case ${i+1} — O'tdi`
          : `Test case ${i+1} — Xato`;
        row.querySelector('.tc-time').textContent = (r.time_ms || '--') + 'ms';
      });

      if (sub.status === 'passed') {
        showSuccess(t, sub);
        _checkEquipmentDrop();
      } else {
        const passed = results.filter(r => r.passed).length;
        showError(passed, results.length || 1);
      }
    } catch(e) {}
  }, 2000);
}

let _lastInvCount = 0;
async function _checkEquipmentDrop() {
  try {
    await new Promise(r => setTimeout(r, 3000));
    const inv = await api.inventory().catch(() => null);
    if (!inv) return;
    const items = Array.isArray(inv) ? inv : [];
    if (_lastInvCount > 0 && items.length > _lastInvCount) {
      const newItems = items.slice(0, items.length - _lastInvCount);
      newItems.forEach(ue => showEquipmentDrop(ue.equipment));
    }
    _lastInvCount = items.length;
  } catch(e) {}
}

function _simulateSubmit(t) {
  const tcs = t.testCases || [];
  if (!tcs.length) { setStatus('ready','Tayyor'); showSuccess(t, null); return; }
  let passed = 0;
  tcs.forEach((_, i) => {
    setTimeout(() => {
      const ms = Math.floor(Math.random() * 60 + 20);
      const ok = Math.random() > 0.15 || t.status === 'done';
      if (ok) passed++;
      const row = document.getElementById('tc' + i);
      if (row) {
        row.className = 'tc-row ' + (ok ? 'tc-pass' : 'tc-fail');
        row.querySelector('.tc-icon').textContent = ok ? '✅' : '❌';
        row.querySelector('.tc-label').textContent = ok
          ? `Test case ${i+1} — O'tdi`
          : `Test case ${i+1} — Xato`;
        row.querySelector('.tc-time').textContent = ms + 'ms';
      }
      if (i === tcs.length - 1) {
        setStatus('ready', 'Tayyor');
        if (passed === tcs.length) showSuccess(t, null);
        else showError(passed, tcs.length);
      }
    }, 400 * (i + 1));
  });
}

function showSuccess(t, sub) {
  const pts = (sub && sub.score_awarded) || t.score || (isProject ? 15 : 10);
  const total = (sub && sub.test_results ? sub.test_results.length : null) || (t.testCases||[]).length || 1;
  showBanner(true, `✅ Barcha test caselar o'tdi — ${total}/${total}`, `+${pts} ball`);
  showAiFeedback(true, t);
  if (isProject) {
    const p = getCurProject(); if (p) { p.done = true; p.score = pts; }
    document.getElementById('projectItem').className = 'mini-proj done';
  } else {
    const tasks = getCurTasks();
    if (tasks[curIdx]) { tasks[curIdx].status = 'done'; tasks[curIdx].score = pts; }
  }
  renderTaskList();
  setTimeout(() => {
    document.getElementById('smIcon').textContent = '🎉';
    document.getElementById('smTitle').textContent = 'Topshiriq qabul qilindi!';
    document.getElementById('smSub').textContent = `${t.name} · Barcha test caselar o'tdi`;
    document.getElementById('smScore').textContent = '+' + pts;
    document.getElementById('scoreModal').classList.add('open');
  }, 800);
}

function showError(passed, total) {
  showBanner(false, `❌ ${passed}/${total} test case o'tdi`, '');
  showAiFeedback(false, isProject ? getCurProject() : getCurTasks()[curIdx]);
}

function showBanner(ok,msg,score){
  const b=document.getElementById('resultBanner');
  b.className='result-banner '+(ok?'success':'error');
  document.getElementById('resultMsg').textContent=msg;
  document.getElementById('resultScore').textContent=score;
  document.getElementById('resultScore').style.display=score?'inline':'none';
}
function hideBanner(){document.getElementById('resultBanner').className='result-banner';}

function showAiFeedback(ok,t){
  const ai=document.getElementById('aiFeedback');
  ai.innerHTML=ok?`
    <div class="ai-bubble">
      <div class="ai-head">🤖 AI Tahlil · Ajoyib!</div>
      <p>Kodingiz barcha test caselardan muvaffaqiyatli o'tdi. <strong>Kuchli tomonlar:</strong> mantiqiy tuzilish to'g'ri, o'zgaruvchilar nomlanishi yaxshi.</p>
    </div>
    <div class="ai-bubble">
      <div class="ai-head">💡 Optimizatsiya</div>
      <p>Kodingizni yanada qisqartirish mumkin. <code>string.Length</code> o'rniga LINQ <code>.Count()</code> ham ishlatsa bo'ladi, ammo <code>Length</code> O(1) — tezroq.</p>
    </div>
    <div class="ai-bubble">
      <div class="ai-head">🚀 Keyingi qadam</div>
      <p>Ushbu mavzu bo'yicha <strong>Advanced darajasi</strong>ni ham sinab ko'ring — u yerda regex bilan string validatsiya mavzusi mavjud.</p>
    </div>`:`
    <div class="ai-bubble">
      <div class="ai-head">🤖 AI Xato tahlili</div>
      <p>Ba'zi test caselar xato chiqdi. Ko'pincha sabab: <strong>bo'sh string</strong> yoki <strong>maxsus belgilar</strong> holati hisoblanmagan.</p>
    </div>
    <div class="ai-bubble">
      <div class="ai-head">💡 Maslahat</div>
      <p>Kiritilgan qiymat bo'sh bo'lishi mumkin. Tekshiring: <code>if (string.IsNullOrEmpty(s))</code> — bu holatni alohida qayta ishlang.</p>
    </div>`;
}

function renderTestCases(){
  const t=isProject ? getCurProject() : getCurTasks()[curIdx];
  if(!t) return;
  document.getElementById('testContent').innerHTML=t.testCases.map((tc,i)=>`
    <div class="tc-row ${tc.pass===true?'tc-pass':tc.pass===false?'tc-fail':'tc-pending'}">
      <div class="tc-icon">${tc.pass===true?'✅':tc.pass===false?'❌':'⏳'}</div>
      <div class="tc-info">
        <div class="tc-label">Test case ${i+1} ${tc.pass===true?"— O'tdi":tc.pass===false?'— Xato':'— Kutilmoqda'}</div>
        <div class="tc-detail">📥 "${tc.inp.replace(/\n/g,' | ')}" → 📤 "${tc.exp}"</div>
      </div>
      <div class="tc-time">${tc.pass!==null?Math.floor(Math.random()*50+20)+'ms':'—'}</div>
    </div>`).join('');
}

function clearOutput(){
  document.getElementById('outputContent').innerHTML='<div class="out-line out-info">// Kodni yozib, ▶ Run bosing yoki ✅ Submit qiling</div><div class="out-line out-info">// Platforma: C# · Judge0 API</div>';
  document.getElementById('aiFeedback').innerHTML='';
  document.getElementById('aiFeedback').classList.remove('show');
  document.getElementById('tab-ai').classList.remove('active');
  document.getElementById('tab-out').classList.add('active');
}

function setStatus(s,t){
  const dot=document.getElementById('statusDot');
  dot.className='sb-dot '+(s==='run'?'sb-run':'sb-ready');
  document.getElementById('statusTxt').textContent=t;
}

function showToast(msg){
  const t=document.createElement('div');
  t.style.cssText='position:fixed;bottom:1.5rem;right:1.5rem;background:#1a1f3a;border:1px solid rgba(108,99,255,0.4);border-radius:12px;padding:.65rem 1rem;font-size:.83rem;font-weight:600;z-index:999;animation:ft .3s ease;box-shadow:0 8px 20px rgba(0,0,0,.3)';
  t.textContent=msg; document.body.appendChild(t);
  setTimeout(()=>t.remove(),2500);
}

const RARITY_COLORS_DROP = {common:'#94a3b8',rare:'#4299e1',epic:'#a855f7',legendary:'#ffd700'};
const RARITY_UZ_DROP     = {common:'Oddiy',rare:'Noyob',epic:'Epic',legendary:'⭐ Afsonaviy'};

function showEquipmentDrop(eq) {
  const col = RARITY_COLORS_DROP[eq.rarity] || '#94a3b8';
  const rar = RARITY_UZ_DROP[eq.rarity] || eq.rarity;
  const bonus = [
    eq.attack_bonus  ? `⚔️ +${eq.attack_bonus}% hujum`  : '',
    eq.defense_bonus ? `🛡️ +${eq.defense_bonus}% himoya` : '',
  ].filter(Boolean).join('  ');

  const el = document.createElement('div');
  el.style.cssText = `position:fixed;top:1.5rem;right:1.5rem;z-index:1000;
    background:linear-gradient(135deg,#0f1628,#1a1f3a);
    border:2px solid ${col};border-radius:18px;padding:1.2rem 1.4rem;
    box-shadow:0 0 30px ${col}44,0 8px 32px rgba(0,0,0,.5);
    animation:dropIn .4s cubic-bezier(.175,.885,.32,1.275);min-width:240px;max-width:300px`;
  el.innerHTML = `
    <div style="font-size:.68rem;font-weight:800;color:${col};letter-spacing:1.5px;text-transform:uppercase;margin-bottom:.5rem">
      🎁 Qurol-Aslaha Topildi!
    </div>
    <div style="display:flex;align-items:center;gap:.9rem;margin-bottom:.6rem">
      <span style="font-size:2.5rem;filter:drop-shadow(0 0 8px ${col})">${eq.icon}</span>
      <div>
        <div style="font-size:1rem;font-weight:800">${eq.name}</div>
        <div style="font-size:.72rem;color:${col};font-weight:700">${rar}</div>
      </div>
    </div>
    <div style="font-size:.78rem;color:#8892b0">${bonus}</div>
    <div style="font-size:.7rem;color:#4a5568;margin-top:.4rem">Profil → Inventar da ko'ring</div>`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

const _st=document.createElement('style');
_st.textContent='@keyframes ft{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}} @keyframes dropIn{from{opacity:0;transform:translateX(20px) scale(.9)}to{opacity:1;transform:none}}';
document.head.appendChild(_st);

function nextTask() {
  closeModal();
  const tasks = getCurTasks();
  if (!isProject && curIdx < tasks.length - 1) loadTask(curIdx + 1);
  else if (!isProject) loadProject();
  else window.location.href = TOPIC_ID ? `mainquest.html?topic=${TOPIC_ID}` : 'mainquest.html';
}
function closeModal() { document.getElementById('scoreModal').classList.remove('open'); }

function _mapTask(t, idx) {
  return {
    id: t.id,
    n: t.order_number || (idx + 1),
    name: t.title || t.name || `Topshiriq ${idx+1}`,
    status: t.is_completed ? 'done' : 'todo',
    score: t.earned_points || null,
    diff: t.difficulty || 'medium',
    desc: t.description || '',
    hint: t.hint || t.solution_hint || '',
    examples: Array.isArray(t.examples) ? t.examples : [],
    methods: t.useful_methods || t.methods || '',
    template: t.template_code || t.starter_code || 'using System;\n\nclass Solution {\n    static void Main() {\n        \n    }\n}',
    testCases: Array.isArray(t.test_cases)
      ? t.test_cases.map(tc => ({ inp: tc.stdin || tc.input || '', exp: tc.expected_output || tc.stdout || '', pass: null }))
      : [],
  };
}
function _mapProject(t) {
  const base = _mapTask(t, 0);
  base.done = t.is_completed || false;
  return base;
}

async function loadTasksFromAPI() {
  if (!TOPIC_ID) return;
  try {
    const [exRes, prRes] = await Promise.all([
      api.tasks({ topic: TOPIC_ID, task_category: 'exercise' }),
      api.tasks({ topic: TOPIC_ID, task_category: 'project' }),
    ]);
    const exercises = Array.isArray(exRes) ? exRes : (exRes.results || []);
    const projects  = Array.isArray(prRes) ? prRes : (prRes.results || []);
    ['beginner', 'intermediate', 'advanced'].forEach(lv => {
      const lvEx = exercises.filter(t => t.level === lv).sort((a,b) => (a.order_number||a.id) - (b.order_number||b.id));
      API_TASKS[lv] = lvEx.map(_mapTask);
      const proj = projects.find(t => t.level === lv);
      if (proj) API_TASKS[lv + '_project'] = _mapProject(proj);
    });
  } catch(e) {
    console.warn('Tasks API xato, demo data ishlatiladi:', e.message);
  }
}

async function initSidequest() {
  Auth.fillUserUI();

  try {
    const me = await api.me();
    const sp = me.student_profile;
    if (sp) {
      document.getElementById('sbRating').textContent = sp.rating_score || 0;
      document.getElementById('sbStreak').textContent = sp.current_streak || 0;
    }
  } catch(e) {}

  if (TOPIC_ID) {
    try {
      const topic = await api.topic(TOPIC_ID);
      const label = `${topic.module_number ? topic.module_number + '-modul · ' : ''}${topic.title || topic.name || ''}`;
      if (label) document.getElementById('tpMeta').textContent = label;
    } catch(e) {}

    await loadTasksFromAPI();

    api.inventory().then(inv => {
      _lastInvCount = Array.isArray(inv) ? inv.length : 0;
    }).catch(() => {});

    try {
      const scRes = await api.topicScore(TOPIC_ID);
      const sc = Array.isArray(scRes) ? scRes[0] : scRes;
      if (sc) {
        LEVEL_LOCKS.intermediate = !sc.beginner_test_passed;
        LEVEL_LOCKS.advanced     = !sc.intermediate_test_passed;
        ['intermediate','advanced'].forEach(lv => {
          const id = lv === 'intermediate' ? 'lvTabO' : 'lvTabY';
          document.getElementById(id).classList.toggle('locked-lv', LEVEL_LOCKS[lv]);
        });
      }
    } catch(e) {}
  }

  switchLevel(INIT_LVL);
}

initSidequest();
