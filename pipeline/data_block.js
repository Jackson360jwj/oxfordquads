const D_ALL=[0,1,2,3,4,5,6], D_WK=[1,2,3,4,5], D_WE=[0,6];
const C = [
{n:"All Souls College",st:"High Street",pc:"OX1 4AL",tel:"01865 279379",web:"https://www.asc.ox.ac.uk/",lat:51.753308,lng:-1.252904,access:"walkin",price:0,
 priceT:"Free",hoursT:"14:00–16:00, Mon–Fri and Sun. Closed all August, and over Easter and Christmas.",
 note:"Front and Great Quadrangles and the Chapel only. Individuals or groups of up to six. The college may close at short notice.",
 win:[{days:[0,1,2,3,4,5],months:[1,2,3,4,5,6,7,9,10,11,12],o:"14:00",c:"16:00"}],dispute:"The University lists Mon-Fri and Sundays; its alumni pages say Monday to Friday only. Sunday is not certain.",advice:["Groups must book ahead rather than turning up.","The college reserves the right to close at short notice."],src:"B"},

{n:"Balliol College",st:"Broad Street",pc:"OX1 3BJ",tel:"01865 277777",web:"https://www.balliol.ox.ac.uk/",lat:51.754951,lng:-1.257892,access:"walkin",price:6,
 priceT:"Adults £6 · concessions and students £3 · free for applicants, Oxford members and alumni",hoursT:"10:00–17:00 daily, or dusk if earlier.",
 note:"Guided groups of 19 plus guide for green and blue badge tours; 7 plus guide otherwise.",tour:"https://www.ox.ac.uk/node/746#where-youll-find-us",
 win:[{days:D_ALL,o:"10:00",c:"17:00"}],ok:"Hours, £6/£3 pricing and group limits all match Balliol’s own visitor page. The college adds that the 8-person group cap applies in term, exam and admissions periods.",advice:["The college asks visitors to phone the lodge before setting out."],telOK:1,src:"B"},

{n:"Blackfriars",st:"St Giles",pc:"OX1 3LY",tel:"01865 278400",web:"https://www.bfriars.ox.ac.uk/",lat:51.756124,lng:-1.260469,access:"walkin",price:0,hall:true,
 priceT:"Free",hoursT:"Church open daily in daylight hours.",note:"A permanent private hall. Public access is to the church.",
 win:[{days:D_ALL,o:"09:00",c:"17:00",approx:true}],src:"A"},

{n:"Brasenose College",st:"Radcliffe Square",pc:"OX1 4AJ",tel:"01865 277830",web:"https://www.bnc.ox.ac.uk/",vis:"https://www.bnc.ox.ac.uk/about-brasenose/for-visitors",lat:51.752972,lng:-1.254747,access:"walkin",price:0,
 priceT:"Free, donations welcome",hoursT:"Mon–Fri 10:00–11:30 and 14:00–16:30 · Sat–Sun 13:00–16:30.",
 note:"Groups book ahead, maximum 20, one group inside at a time. Individuals are admitted at the duty porter's discretion.",tour:"https://www.ox.ac.uk/node/747#where-youll-find-us",
 win:[{days:D_WK,o:"10:00",c:"11:30"},{days:D_WK,o:"14:00",c:"16:30"},{days:D_WE,o:"13:00",c:"16:30"}],ok:"Hours, free entry and group rules all match Brasenose’s own visiting page.",advice:["The college asks visitors to phone the lodge before setting out.","Contact the college in advance to confirm it is open.","The college reserves the right to close at short notice."],telOK:1,src:"A"},

{n:"Campion Hall",st:"Brewer Street",pc:"OX1 1QS",tel:"01865 286100",web:"https://www.campion.ox.ac.uk/",lat:51.749590,lng:-1.258323,access:"appointment",price:null,hall:true,
 priceT:"—",hoursT:"By appointment only.",note:"A permanent private hall.",src:"A"},

{n:"Christ Church",st:"St Aldate's",pc:"OX1 1DP",tel:"01865 276492",web:"https://www.chch.ox.ac.uk/visit-us",vis:"https://www.chch.ox.ac.uk/visit/tickets-and-information",lat:51.750412,lng:-1.254967,access:"book",price:null,
 priceT:"Timed ticket — adults around £20, roughly £2 less booked online, with a reduced rate 25 June–1 September 2026. Concessions available. Check the college site for the exact rate.",
 hoursT:"Mon–Sat 10:00–17:00, Sun 14:00–17:00, last entry 16:15. Timed ticket, booked online; tickets released weekly.",
 fix:"The University's page gives no opening times and no prices for Christ Church at all. Times added from the University's alumni pages, price band from the college's ticketing pages.",
 note:"Book online to guarantee entry; groups of 12 or more must book. The Hall and Cathedral occasionally close without notice — check the known closures page. Tickets also sold at the Visitor Centre in Christ Church Meadow.",tour:"https://www.ox.ac.uk/node/748#where-youll-find-us",advice:["Closes for events, exams and ceremonies during the year."],src:"B"},

{n:"Corpus Christi College",st:"Merton Street",pc:"OX1 4JF",tel:"01865 276700",web:"https://www.ccc.ox.ac.uk/",lat:51.750599,lng:-1.253584,access:"walkin",price:0,
 priceT:"Free",hoursT:"13:30–16:30 daily, subject to college events and exams.",
 note:"Groups of up to 20 must book ahead and be accompanied by a Blue Badge Guide.",tour:"https://www.ox.ac.uk/node/749#where-youll-find-us",
 win:[{days:D_ALL,o:"13:30",c:"16:30"}],dispute:"The University lists 13:30-16:30 and groups of 20; its alumni pages say 14:00-17:00 and groups of 19.",advice:["The college asks visitors to phone the lodge before setting out.","Contact the college in advance to confirm it is open.","Closes for events, exams and ceremonies during the year."],telOK:1,src:"B"},

{n:"Exeter College",st:"Turl Street",pc:"OX1 3DP",tel:"01865 279600",web:"http://www.exeter.ox.ac.uk/",vis:"https://www.exeter.ox.ac.uk/tour/",lat:51.753875,lng:-1.255508,access:"book",price:4,
 priceT:"£4 · under-12s free · Bodleian and Oxford alumni card holders free, 14:00–17:00",
 hoursT:"General visitors only outside term time and only with a pre-booked tour group. Applicants and Exeter alumni: free, daily 09:00–17:00.",
 note:"Call the lodge to check the college is open before you travel. The library is closed to visitors. Cohen Quad is not generally open to the public. Chapel services are open to all.",tour:"https://www.ox.ac.uk/node/750#where-youll-find-us",dispute:"Sources conflict badly, including two of Exeter’s own pages: one says the public may walk in 14:00-17:00 out of term for £4, the other says only with a pre-booked tour group. Call before travelling.",advice:["The college asks visitors to phone the lodge before setting out.","Closes for events, exams and ceremonies during the year."],telOK:1,src:"B"},

{n:"Green Templeton College",st:"Woodstock Road",pc:"OX2 6HG",tel:"01865 274770",web:"https://www.gtc.ox.ac.uk/",lat:51.761253,lng:-1.263395,access:"appointment",price:null,grad:true,
 priceT:"—",hoursT:"By appointment only.",note:"Graduate college. Maximum 20 people in a group.",src:"A"},

{n:"Harris Manchester College",st:"Mansfield Road",pc:"OX1 3TD",tel:"01865 271006",web:"https://www.hmc.ox.ac.uk/",lat:51.755600,lng:-1.252395,access:"walkin",price:0,
 priceT:"Free, donations welcome",hoursT:"Chapel only, when available. Mon–Fri 10:00–17:30 · Sat 08:30–20:00.",
 note:"Large parties must book in advance.",tour:"https://www.ox.ac.uk/node/751#where-youll-find-us",
 win:[{days:D_WK,o:"10:00",c:"17:30"},{days:[6],o:"08:30",c:"20:00"}],dispute:"The University lists Sat 08:30-20:00; its alumni pages say Mon-Fri 08:30-17:30 and Sat 09:00-12:00.",src:"B"},

{n:"Hertford College",st:"Catte Street",pc:"OX1 3BW",tel:"01865 279400",web:"https://www.hertford.ox.ac.uk/",lat:51.754421,lng:-1.253595,access:"restricted",price:null,
 priceT:"—",hoursT:"Applicants and alumni may visit the main quad. All other visitors by appointment.",
 note:"Major building work continues until summer 2027, so entry is sometimes restricted — ask at the lodge first. Chapel services and recitals in term are open to everyone.",dispute:"The University says other visitors are by appointment; its alumni pages say card holders may see OB Quad and the Chapel 10:00-15:00.",src:"B"},

{n:"Jesus College",st:"Turl Street",pc:"OX1 3DW",tel:"01865 279700",web:"https://www.jesus.ox.ac.uk/",lat:51.753452,lng:-1.257304,access:"book",price:3,
 priceT:"Adults £3 · seniors and children over 5 £2",hoursT:"Pre-booked guided tours only, 14:00–16:30 daily.",
 note:"Maximum 20 people in a group; groups must book ahead. Other enquiries to the lodge.",tour:"https://realsee.ai/ybkk6wwp?floorSwitch=0",src:"B"},

{n:"Keble College",st:"Parks Road",pc:"OX1 3PG",tel:"01865 272727",web:"https://www.keble.ox.ac.uk/",vis:"https://www.keble.ox.ac.uk/visiting-keble/",lat:51.758713,lng:-1.257998,access:"walkin",price:0,
 priceT:"Free",hoursT:"14:00–17:00 daily.",
 note:"Liddon Quad and the Chapel. Alumni, applicants and offer holders may visit any time. Small groups at the porters' discretion. No animals except assistance dogs.",tour:"https://www.ox.ac.uk/node/754#where-youll-find-us",
 win:[{days:D_ALL,o:"14:00",c:"17:00"}],email:"porters.lodge@keble.ox.ac.uk",advice:["The college asks visitors to phone the lodge before setting out.","Contact the college in advance to confirm it is open.","Closes for events, exams and ceremonies during the year."],src:"A"},

{n:"Kellogg College",st:"60–62 Banbury Road",pc:"OX2 6PN",tel:"01865 612000",web:"https://www.kellogg.ox.ac.uk/",lat:51.764356,lng:-1.259701,access:"walkin",price:0,grad:true,
 priceT:"Free",hoursT:"Mon–Fri 09:00–17:00.",note:"Graduate college.",
 win:[{days:D_WK,o:"09:00",c:"17:00"}],src:"A"},

{n:"Lady Margaret Hall",st:"Norham Gardens",pc:"OX2 6QA",tel:"01865 274300",web:"https://www.lmh.ox.ac.uk/",lat:51.765793,lng:-1.252851,access:"walkin",price:0,
 priceT:"Free",hoursT:"10:00–17:00 daily.",tour:"https://www.ox.ac.uk/node/755#where-youll-find-us",
 win:[{days:D_ALL,o:"10:00",c:"17:00"}],src:"A"},

{n:"Linacre College",st:"St Cross Road",pc:"OX1 3JA",tel:"01865 271650",web:"https://www.linacre.ox.ac.uk/",lat:51.759332,lng:-1.249699,access:"appointment",price:null,grad:true,
 priceT:"—",hoursT:"By appointment only.",note:"Graduate college.",src:"A"},

{n:"Lincoln College",st:"Turl Street",pc:"OX1 3DR",tel:"01865 279800",web:"https://www.lincoln.ox.ac.uk/",vis:"https://www.lincoln.ox.ac.uk/discover/the-college/visiting-lincoln/",lat:51.752894,lng:-1.255641,access:"walkin",price:0,
 priceT:"Free",hoursT:"14:00–17:00 daily.",
 note:"Evensong is free and open to all; see the chapel services page.",tour:"https://lincoln.ox.ac.uk/virtual-tour",
 win:[{days:D_ALL,o:"14:00",c:"17:00"}],email:"info@lincoln.ox.ac.uk",advice:["Contact the college in advance to confirm it is open."],telOK:1,src:"B"},

{n:"Magdalen College",st:"High Street",pc:"OX1 4AU",tel:"01865 276000",web:"https://www.magd.ox.ac.uk/visiting-magdalen-college/",vis:"https://www.magd.ox.ac.uk/about-magdalen-college/visiting-magdalen-college/",lat:51.753348,lng:-1.244472,access:"walkin",price:10,
 priceT:"Adults £10 · over-65s, children and students £9 · family £28",
 hoursT:"10:00 to dusk or 17:00, whichever is earlier. July, August and September: closes 18:30.",
 note:"Open 10:00–13:00 only on 24 September 2026. Closed 25 September and 4 October 2026, and 22–31 December. Open free on 1 January, 10:00–15:30. Check the college site for changes.",tour:"https://www.ox.ac.uk/node/757#where-youll-find-us",
 win:[{days:D_ALL,months:[1,2,3,4,5,6,10,11,12],o:"10:00",c:"17:00"},{days:D_ALL,months:[7,8,9],o:"10:00",c:"18:30"}],ok:"Hours and all three prices match Magdalen’s own visitor page.",advice:["The college asks visitors to phone the lodge before setting out.","Groups must book ahead rather than turning up."],telOK:1,src:"B"},

{n:"Mansfield College",st:"Mansfield Road",pc:"OX1 3TF",tel:"01865 270999",web:"https://www.mansfield.ox.ac.uk/",lat:51.757347,lng:-1.252970,access:"walkin",price:0,
 priceT:"Free, donations welcome",hoursT:"Mon–Fri 09:00–17:00.",
 note:"Grounds, Chapel and the Crypt cafeteria. Other buildings by appointment. Groups of up to 12, with a guide.",tour:"https://www.ox.ac.uk/node/758#where-youll-find-us",
 win:[{days:D_WK,o:"09:00",c:"17:00"}],email:"porter@mansfield.ox.ac.uk",src:"B"},

{n:"Merton College",st:"Merton Street",pc:"OX1 4JD",tel:"01865 276310",web:"https://www.merton.ox.ac.uk/",lat:51.751099,lng:-1.250699,access:"walkin",price:5,
 priceT:"Adults £5 · ages 13–17 and 65+ £3 · under-13s, Oxford members and alumni free · guided tour with the medieval library £10 (summer)",
 hoursT:"Mon–Fri 14:00–17:00 · Sat 10:00–17:00 · Sun 12:00–17:00. Last entry 16:30.",
 note:"Groups of 15 or fewer need not book. Card payment only at the lodge, no cash. Under-16s must be accompanied. Assistance dogs welcome.",tour:"https://www.ox.ac.uk/node/759#where-youll-find-us",
 win:[{days:D_WK,o:"14:00",c:"17:00"},{days:[6],o:"10:00",c:"17:00"},{days:[0],o:"12:00",c:"17:00"}],dispute:"The University lists Sunday from 12:00; its alumni pages say Saturday and Sunday both from 10:00.",advice:["Contact the college in advance to confirm it is open.","Closes for events, exams and ceremonies during the year.","The college reserves the right to close at short notice."],src:"B"},

{n:"New College",st:"New College Lane",pc:"OX1 3BN",tel:"01865 279544",web:"https://www.new.ox.ac.uk/",vis:"https://www.new.ox.ac.uk/visiting-the-college",lat:51.754044,lng:-1.251088,access:"walkin",price:12,
 priceT:"Adults £12 · concessions (seniors, under-16s, students) £11 · family £32 · free: under-7s, Oxford city residents, old members, applicants, and Bodleian or alumni card holders plus two guests",
 hoursT:"10 March–31 October: 10:00–17:00 daily, last entry 16:30. 1 November–9 March: closed Mondays; Tue–Fri and Sun 13:30–16:30; Sat 10:00–16:30.",
 note:"Advance booking only for groups of 10 or more. Maximum 20 per group; larger groups split. Card payment only.",tour:"https://www.ox.ac.uk/node/760#where-youll-find-us",
 fix:"The University's page lists the concession as £10 and gives no separate Saturday winter hours. Corrected from New College's own visitor page.",
 win:[{days:D_ALL,months:[4,5,6,7,8,9,10],o:"10:00",c:"17:00"},{days:[0,2,3,4,5],months:[11,12,1,2,3],o:"13:30",c:"16:30"},{days:[6],months:[11,12,1,2,3],o:"10:00",c:"16:30"}],email:"tourism@new.ox.ac.uk",advice:["Contact the college in advance to confirm it is open."],telOK:1,src:"B"},

{n:"Nuffield College",st:"New Road",pc:"OX1 1NF",tel:"01865 278500",web:"https://www.nuffield.ox.ac.uk/",lat:51.752729,lng:-1.262658,access:"closed",price:null,grad:true,
 priceT:"—",hoursT:"Currently closed to visitors.",note:"Graduate college.",email:"info@nuffield.ox.ac.uk",src:"A"},

{n:"Oriel College",st:"Oriel Square",pc:"OX1 4EW",tel:"01865 276555",web:"https://www.oriel.ox.ac.uk/",lat:51.751826,lng:-1.253843,access:"walkin",price:3,
 priceT:"Adults £3 · concessions £2",hoursT:"14:00–17:00 daily, or dusk if earlier.",
 note:"Hall, chapel and first quad only. Maximum 12 in a group. Closed during events.",tour:"https://www.ox.ac.uk/node/761#where-youll-find-us",
 win:[{days:D_ALL,o:"14:00",c:"17:00"}],email:"lodge@oriel.ox.ac.uk",advice:["Contact the college in advance to confirm it is open.","Groups must book ahead rather than turning up."],src:"B"},

{n:"Pembroke College",st:"Pembroke Square, St Aldate's",pc:"OX1 1DW",tel:"01865 276444",web:"http://www.pmb.ox.ac.uk/",lat:51.750226,lng:-1.258115,access:"restricted",price:null,
 priceT:"—",hoursT:"Not open to the public.",
 note:"Applicants, alumni and members of the University are welcome. Other visits can sometimes be arranged by appointment.",tour:"https://www.ox.ac.uk/node/762#where-youll-find-us",src:"A"},

{n:"The Queen's College",st:"High Street",pc:"OX1 4AW",tel:"01865 279120",web:"http://www.queens.ox.ac.uk/",lat:51.753276,lng:-1.251414,access:"book",price:0,
 priceT:"Free",hoursT:"Pre-arranged tours only.",
 note:"Open to applicants, alumni, University members and those with a college connection. Otherwise entry is only on a tour with the Oxford Guild of Tour Guides, or to attend Evensong.",tour:"https://www.ox.ac.uk/node/763#where-youll-find-us",src:"A"},

{n:"Regent's Park College",st:"Pusey Street",pc:"OX1 2LB",tel:"01865 288120",web:"https://www.rpc.ox.ac.uk/",lat:51.756866,lng:-1.260903,access:"appointment",price:0,
 priceT:"Free, £2 donation suggested",hoursT:"By appointment.",email:"enquiries@regents.ox.ac.uk",src:"A"},

{n:"Reuben College",st:"Parks Road",pc:"OX1 3QP",tel:"01865 616477",web:"https://reuben.ox.ac.uk/",lat:51.758010,lng:-1.255788,access:"appointment",price:0,grad:true,
 priceT:"Free",hoursT:"By invitation only, except 13:00–14:00 daily when University members may lunch in the Dining Hall.",note:"Graduate college.",src:"A"},

{n:"St Anne's College",st:"Woodstock Road",pc:"OX2 6HS",tel:"01865 274800",web:"https://www.st-annes.ox.ac.uk/",lat:51.762006,lng:-1.261758,access:"walkin",price:0,
 priceT:"Free, donations welcome",hoursT:"09:00–17:00 daily.",note:"Large groups must book in advance.",tour:"https://www.ox.ac.uk/node/765#where-youll-find-us",
 win:[{days:D_ALL,o:"09:00",c:"17:00"}],src:"A"},

{n:"St Antony's College",st:"Woodstock Road",pc:"OX2 6JF",tel:"01865 284700",web:"https://www.sant.ox.ac.uk/",lat:51.763282,lng:-1.262824,access:"walkin",price:0,grad:true,
 priceT:"Free",hoursT:"08:00–17:00 daily.",note:"Graduate college.",
 win:[{days:D_ALL,o:"08:00",c:"17:00"}],src:"A"},

{n:"St Catherine's College",st:"Manor Road",pc:"OX1 3UJ",tel:"01865 271700",web:"https://www.stcatz.ox.ac.uk/",lat:51.756559,lng:-1.244929,access:"closed",price:0,
 priceT:"Free",hoursT:"No tours during the final phases of restoration work.",
 note:"The porters' lodge is staffed 24 hours a day for general enquiries.",tour:"https://www.ox.ac.uk/node/766#where-youll-find-us",dispute:"The University says no tours during restoration; its alumni pages say the college is open 09:00-17:00 daily to University card holders.",email:"lodge@stcatz.ox.ac.uk",src:"B"},

{n:"St Cross College",st:"St Giles",pc:"OX1 3LZ",tel:"01865 278490",web:"https://www.stx.ox.ac.uk/",lat:51.756444,lng:-1.260708,access:"appointment",price:null,grad:true,
 priceT:"—",hoursT:"By appointment only.",note:"Graduate college.",tour:"https://stx.web.ox.ac.uk/take-a-tour",src:"A"},

{n:"St Edmund Hall",st:"Queen's Lane",pc:"OX1 4AR",tel:"01865 279000",web:"https://www.seh.ox.ac.uk/",lat:51.753129,lng:-1.249765,access:"walkin",price:2,
 priceT:"Summer charge £2 · under-14s free",hoursT:"10:00–16:00 daily, except during events and exams.",
 note:"Applicants, alumni and University members welcome. Groups of up to 10, by appointment.",tour:"https://www.ox.ac.uk/node/767#where-youll-find-us",
 win:[{days:D_ALL,o:"10:00",c:"16:00"}],email:"lodge@seh.ox.ac.uk",src:"B"},

{n:"St Hilda's College",st:"Cowley Place",pc:"OX4 1DY",tel:"01865 276884",web:"https://www.st-hildas.ox.ac.uk/",lat:51.748435,lng:-1.246030,access:"appointment",price:0,
 priceT:"Free",hoursT:"By appointment only.",tour:"https://www.ox.ac.uk/node/768#where-youll-find-us",dispute:"The University says appointment only; its alumni pages say the college is open 08:00-17:00 daily to University card holders.",email:"enquiries@st-hildas.ox.ac.uk",src:"B"},

{n:"St Hugh's College",st:"St Margaret's Road",pc:"OX2 6LE",tel:"01865 274900",web:"http://www.st-hughs.ox.ac.uk/",lat:51.766367,lng:-1.263210,access:"book",price:0,pill:"Call first",
 priceT:"Free, donations welcome",hoursT:"Visitors are welcome, but check in advance by phone or email.",tour:"https://www.ox.ac.uk/node/769#where-youll-find-us",dispute:"The University says to check in advance; its alumni pages say the college is open to all visitors free, 09:00-17:30, seven days a week.",src:"B"},

{n:"St John's College",st:"St Giles'",pc:"OX1 3JP",tel:"01865 277300",web:"https://www.sjc.ox.ac.uk/",lat:51.757198,lng:-1.257652,access:"walkin",price:0,
 priceT:"Free",hoursT:"13:00–17:00, or dusk if earlier. Chapel from 13:30, closed Wednesdays.",
 note:"Groups of up to 14 with a guide; larger groups are split.",tour:"https://www.ox.ac.uk/node/770#where-youll-find-us",
 win:[{days:D_ALL,o:"13:00",c:"17:00"}],telOK:1,src:"B"},

{n:"St Peter's College",st:"New Inn Hall Street",pc:"OX1 2DL",tel:"01865 278900",web:"https://www.spc.ox.ac.uk/",lat:51.752485,lng:-1.261023,access:"walkin",price:0,
 priceT:"Free, donations welcome",hoursT:"10:00–17:00, though hours vary — call to check.",
 note:"Groups of five or more must book.",tour:"https://www.ox.ac.uk/node/771#where-youll-find-us",
 win:[{days:D_ALL,o:"10:00",c:"17:00",approx:true}],email:"porters.lodge@spc.ox.ac.uk",advice:["The college asks visitors to phone the lodge before setting out."],src:"B"},

{n:"Somerville College",st:"Woodstock Road",pc:"OX2 6HD",tel:"01865 270600",web:"https://www.some.ox.ac.uk/",lat:51.759000,lng:-1.262845,access:"walkin",price:0,
 priceT:"Free, donations welcome",hoursT:"Term time only: 09:00–12:00 and 14:00–16:00. Out of term, University members and alumni card holders only.",
 note:"Large groups must book in advance.",tour:"https://www.ox.ac.uk/node/772#where-youll-find-us",
 win:[{days:D_ALL,term:"term",o:"09:00",c:"12:00"},{days:D_ALL,term:"term",o:"14:00",c:"16:00"}],email:"enquiries@some.ox.ac.uk",src:"B"},

{n:"Trinity College",st:"Broad Street",pc:"OX1 3BH",tel:"01865 279900",web:"https://www.trinity.ox.ac.uk/",lat:51.755377,lng:-1.256890,access:"walkin",price:7,
 priceT:"Adults £7 · concessions and students £5 · groups £5 each · under-12s free",
 hoursT:"Term: 10:00–12:00 and 14:00–17:00. Out of term: 10:00–12:00 and 13:00–17:00.",
 note:"Call ahead in summer — the college closes for events.",tour:"https://www.ox.ac.uk/node/773#where-youll-find-us",
 win:[{days:D_ALL,term:"term",o:"10:00",c:"12:00"},{days:D_ALL,term:"term",o:"14:00",c:"17:00"},
      {days:D_ALL,term:"vac",o:"10:00",c:"12:00"},{days:D_ALL,term:"vac",o:"13:00",c:"17:00"}],ok:"Term and vacation hours match Trinity’s own visiting page exactly.",advice:["The college asks visitors to phone the lodge before setting out."],telOK:1,src:"B"},

{n:"University College",st:"High Street",pc:"OX1 4BH",tel:"01865 276602",web:"https://www.univ.ox.ac.uk/",lat:51.752078,lng:-1.251371,access:"walkin",price:5,
 priceT:"Adults £5 · concessions £3 · free for Bodleian card holders, Univ alumni, applicants and under-8s",
 hoursT:"10:00–12:00 and 14:00–16:00, seven days a week. Closed for events.",
 note:"Large parties must book in advance.",tour:"https://www.ox.ac.uk/node/774#where-youll-find-us",
 win:[{days:D_ALL,o:"10:00",c:"12:00"},{days:D_ALL,o:"14:00",c:"16:00"}],email:"lodge@univ.ox.ac.uk",src:"B"},

{n:"Wadham College",st:"Parks Road",pc:"OX1 3PN",tel:"01865 277900",web:"https://www.wadham.ox.ac.uk/",vis:"https://www.wadham.ox.ac.uk/groups-visiting-wadham-college",lat:51.756222,lng:-1.254100,access:"walkin",price:0,
 priceT:"Free",hoursT:"Term: 13:00–16:15. Out of term: 10:30–11:45 and 13:00–16:15.",
 tour:"https://www.ox.ac.uk/admissions/undergraduate/college-life/college-listing/wadham-college#virtual-tour",
 win:[{days:D_ALL,term:"term",o:"13:00",c:"16:15"},
      {days:D_ALL,term:"vac",o:"10:30",c:"11:45"},{days:D_ALL,term:"vac",o:"13:00",c:"16:15"}],ok:"Term and vacation hours match Wadham’s own group-visits page exactly.",email:"lodge@wadham.ox.ac.uk",advice:["The college reserves the right to close at short notice."],src:"B"},

{n:"Wolfson College",st:"Linton Road",pc:"OX2 6UD",tel:"01865 274100",web:"https://www.wolfson.ox.ac.uk/",lat:51.771822,lng:-1.254572,access:"walkin",price:0,grad:true,
 priceT:"Free",hoursT:"Daylight hours.",note:"Graduate college. Groups should tell the college they are coming.",
 win:[{days:D_ALL,o:"09:00",c:"17:00",approx:true}],src:"A"},

{n:"Worcester College",st:"Walton Street",pc:"OX1 2HB",tel:"01865 278300",web:"https://www.worc.ox.ac.uk/",lat:51.755396,lng:-1.266569,access:"restricted",price:0,
 priceT:"Free",hoursT:"12:30–16:00 daily for University members, alumni, applicants and residents of OX1 and OX2.",
 note:"Everyone else needs an official tour. Maximum 6 in a group. No booking — sign in at the lodge.",tour:"https://www.ox.ac.uk/node/776#where-youll-find-us",src:"A"},

{n:"Wycliffe Hall",st:"Banbury Road",pc:"OX2 6PW",tel:"01865 274200",web:"https://www.wycliffe.ox.ac.uk/",lat:51.762645,lng:-1.259745,access:"appointment",price:0,hall:true,
 priceT:"Free",hoursT:"By appointment.",note:"A permanent private hall.",tour:"https://www.ox.ac.uk/node/777#where-youll-find-us",telOK:1,src:"A"}
];

