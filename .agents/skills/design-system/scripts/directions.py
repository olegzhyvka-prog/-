"""Єдине джерело візуальних мов. Імпортують і дошка референсів, і генератор сайту —
тому прев'ю на дошці й готовий лендінг гарантовано в одній мові."""

D = [
 dict(n=1, name="Editorial", note="журнальний · послуги, консалтинг, авторське",
      bg="#FBFAF7", fg="#16150F", mut="#6B6559", acc="#B4501E", line="#E2DDD2",
      hf="'Iowan Old Style','Palatino Linotype',Georgia,serif", r="0px",
      btn="solid", align="left", extra="rule"),
 dict(n=2, name="Warm Minimal", note="теплий мінімалізм · спокій, здоров'я, освіта",
      bg="#FAF7F2", fg="#2A2622", mut="#6E675E", acc="#3F6B4A", line="#E8E0D4",
      hf="ui-sans-serif,system-ui,sans-serif", r="16px",
      btn="solid", align="left", extra="pad"),
 dict(n=3, name="Bento", note="модульна сітка · SaaS з багатьма функціями",
      bg="#F6F7F9", fg="#111418", mut="#69707A", acc="#2563EB", line="#E7EAEE",
      hf="ui-sans-serif,system-ui,sans-serif", r="18px",
      btn="solid", align="left", extra="bento"),
 dict(n=4, name="Technical", note="точний · інструменти, API, для інженерів",
      bg="#FFFFFF", fg="#0F1115", mut="#5C6470", acc="#0B7285", line="#E3E6E9",
      hf="ui-sans-serif,system-ui,sans-serif", r="5px",
      btn="outline", align="left", extra="mono"),
 dict(n=5, name="Bold Color", note="плакатний · споживче, емоція",
      bg="#F4E04D", fg="#171203", mut="#4A4114", acc="#171203", line="#DFC93C",
      hf="ui-sans-serif,system-ui,sans-serif", r="999px",
      btn="solid", align="left", extra="poster"),
 dict(n=6, name="Soft Product", note="м'який продуктовий · B2C SaaS, найбезпечніший",
      bg="#FFFFFF", fg="#1C2434", mut="#67718A", acc="#4F7DF3", line="#E6ECF7",
      hf="ui-sans-serif,system-ui,sans-serif", r="14px",
      btn="solid", align="left", extra="shot"),
 dict(n=7, name="Archive", note="паперовий · контент, спільноти, курси",
      bg="#F0EBE1", fg="#2B2620", mut="#6D6357", acc="#7A3E2F", line="#D8CFBE",
      hf="'Iowan Old Style',Georgia,serif", r="0px",
      btn="dashed", align="left", extra="paper"),
 dict(n=8, name="Night", note="темний · ТІЛЬКИ нічні продукти: dev-tools, монтаж, трейдинг",
      bg="#14161A", fg="#E8EAED", mut="#98A0AC", acc="#5EE7C4", line="#262A31",
      hf="ui-sans-serif,system-ui,sans-serif", r="8px",
      btn="solid", align="left", extra="mono"),
]


def by_number(n):
    for d in D:
        if d["n"] == int(n):
            return d
    raise SystemExit(f"Немає напряму {n}. Доступні: {[x['n'] for x in D]}")
