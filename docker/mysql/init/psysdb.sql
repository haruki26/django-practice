-- /*================================================================*/
-- /*  応用研修 テーブル/データ作成スクリプト                2024.09 */
-- /*    データベース：psysdb
-- /*================================================================*/

-- /*================================================================*/
-- /*  psysdbデーターベースの作成                                    */
-- /*================================================================*/
drop database if exists psysdb;
create database psysdb;

use psysdb;


-- /*================================================================*/
-- /*  得意先採番テーブル（customer_numbering）テーブル削除          */
-- /*================================================================*/

DROP TABLE IF EXISTS customer_numbering;


-- /*================================================================*/
-- /*  受注明細（order_details）テーブル削除                         */
-- /*================================================================*/

DROP TABLE IF EXISTS order_details;


-- /*================================================================*/
-- /*  受注（order）テーブル削除                                     */
-- /*================================================================*/

DROP TABLE IF EXISTS orders;


-- /*================================================================*/
-- /*  得意先（customer）テーブル削除                                */
-- /*================================================================*/

DROP TABLE IF EXISTS customer;


-- /*================================================================*/
-- /*  従業員（employee）テーブル削除                                */
-- /*================================================================*/

DROP TABLE IF EXISTS employee;


-- /*================================================================*/
-- /*  商品（item）テーブル削除                                      */
-- /*================================================================*/

DROP TABLE IF EXISTS item;


-- /*================================================================*/
-- /*  得意先採番テーブル（customer_numbering）テーブル作成          */
-- /*================================================================*/

CREATE TABLE customer_numbering (
  customer_code INTEGER(4) NOT NULL
);


-- /*================================================================*/
-- /*  得意先（customer）テーブル作成                                */
-- /*================================================================*/

CREATE TABLE customer (
 customer_code VARCHAR(6) not null,
 customer_name VARCHAR(32),
 customer_telno VARCHAR(13),
 customer_postalcode VARCHAR(8),
 customer_address VARCHAR(40),
 discount_rate INTEGER(2),
 delete_flag INTEGER(1) NOT NULL,
 PRIMARY KEY(customer_code)
);


-- /*================================================================*/
-- /*  従業員（employee）テーブル作成                                */
-- /*================================================================*/

CREATE TABLE employee (
  employee_no VARCHAR(6) NOT NULL,
  employee_name VARCHAR(32),
  password VARCHAR(8),
  PRIMARY KEY(employee_no)
);


-- /*================================================================*/
-- /*  商品（item）テーブル作成                                      */
-- /*================================================================*/

CREATE TABLE item (
  item_code VARCHAR(6) NOT NULL,
  item_name VARCHAR(32),
  price INTEGER(6),
  stock INTEGER(8),
  PRIMARY KEY(item_code)
);


-- /*================================================================*/
-- /*  受注（orders）テーブル作成                                    */
-- /*================================================================*/

CREATE TABLE orders (
  order_no VARCHAR(6) NOT NULL,
  customer_code VARCHAR(6),
  employee_no VARCHAR(6),
  total_price INTEGER(12),
  detail_num INTEGER(2),
  deliver_date date,
  order_date date,
  PRIMARY KEY(order_no),
  FOREIGN KEY (customer_code) REFERENCES customer(customer_code),
  FOREIGN KEY (employee_no) REFERENCES employee(employee_no)
);


-- /*================================================================*/
-- /*  受注明細（order_details）テーブル作成                         */
-- /*================================================================*/

CREATE TABLE order_details (
  order_no VARCHAR(6) NOT NULL,
  item_code VARCHAR(6) not null,
  order_num INTEGER(4),
  order_price INTEGER(10),
  PRIMARY KEY(order_no,item_code),
  FOREIGN KEY (order_no) REFERENCES orders(order_no),
  FOREIGN KEY (item_code) REFERENCES item(item_code)
);


-- /*================================================================*/
-- /*  得意先採番（customer_numbering）テーブル データ挿入           */
-- /*================================================================*/

INSERT INTO customer_numbering VALUES(15);


-- /*================================================================*/
-- /*  得意先（customer）テーブル データ挿入                         */
-- /*================================================================*/

INSERT INTO customer VALUES('RA0001','A店社','06-128-3581','530-0001','大阪市北区梅田２－１',0,0);
INSERT INTO customer VALUES('RA0002','B店社','06-128-3582','530-0002','大阪市北区中之島２－２',0,0);
INSERT INTO customer VALUES('RA0003','C店社','06-128-3583','530-0003','大阪市北区弁天２－１',0,0);
INSERT INTO customer VALUES('RA0004','D店社','06-128-3584','530-0004','大阪市北区南幸１－４',0,0);
INSERT INTO customer VALUES('RA0005','E店社','06-128-3585','530-0005','大阪市北区梅田２－５',0,0);
INSERT INTO customer VALUES('RA0006','F店社','06-128-3586','530-0006','大阪市北区梅田２－６',0,0);
INSERT INTO customer VALUES('RA0007','G店社','06-128-3587','530-0007','大阪市北区堂島１－１',0,0);
INSERT INTO customer VALUES('RA0008','H店社','06-128-3588','530-0008','大阪市北区堂島１－２',0,0);
INSERT INTO customer VALUES('RA0009','I店社','06-128-3589','530-0009','大阪市北区堂島２－３',0,0);
INSERT INTO customer VALUES('RA0010','J店社','06-150-3590','530-0010','大阪市北区堂島２－４',0,0);
INSERT INTO customer VALUES('RA0011','K店社','06-150-3591','530-0011','大阪市北区弁天２－１',0,0);
INSERT INTO customer VALUES('RA0012','L店社','06-150-3592','530-0012','大阪市北区弁天２－２',0,0);
INSERT INTO customer VALUES('RA0013','M店社','06-150-3593','530-0013','大阪市北区弁天２－３',0,0);
INSERT INTO customer VALUES('RA0014','N店社','06-150-3594','530-0014','大阪市北区弁天２－４',0,0);
INSERT INTO customer VALUES('RA0015','O店社','06-150-3595','530-0015','大阪市北区弁天２－５',0,0);



-- /*================================================================*/
-- /*  従業員（employee）テーブル データ挿入                         */
-- /*================================================================*/

INSERT INTO employee VALUES('R20001','鈴木一郎','ry000001');
INSERT INTO employee VALUES('R20002','山田太郎','rx000002');
INSERT INTO employee VALUES('R20003','坂本竜馬','rw000003');
INSERT INTO employee VALUES('R20004','田中花','rv000004');


-- /*================================================================*/
-- /*  商品（item）テーブル データ挿入                               */
-- /*================================================================*/

INSERT INTO item VALUES('AR0001','ミネラルウォーター（500ml）',80 ,99975); 
INSERT INTO item VALUES('AR0002','ミネラルウォーター（2ｌ）',100 ,100000); 
INSERT INTO item VALUES('AR0003','ミネラルウォーター（業務用）',1000 ,100000); 
INSERT INTO item VALUES('AR0004','ミネラルウォーター(500ml)x12本',500 ,100000); 
INSERT INTO item VALUES('AR0005','ミネラルウォーター(2ｌ)x12本',1200 ,100000); 
INSERT INTO item VALUES('AR0006','海洋深層水（500ml）',80 ,100000); 
INSERT INTO item VALUES('AR0007','海洋深層水（2ｌ）',100 ,100000); 
INSERT INTO item VALUES('AR0008','海洋深層水（業務用）',1000 ,100000); 
INSERT INTO item VALUES('AR0009','海洋深層水(500ml)x12本',500 ,100000); 
INSERT INTO item VALUES('AR0010','海洋深層水(2ｌ)x12本',1200 ,100000);
INSERT INTO item VALUES('BR0001','黄金にんにく・10日分',1200 ,99970); 
INSERT INTO item VALUES('BR0002','黄金にんにく・30日分',3000 ,99990); 
INSERT INTO item VALUES('BR0003','黄金にんに・ 90日分',8000 ,100000); 
INSERT INTO item VALUES('BR0004','無臭にんにく・10日分',1000 ,100000); 
INSERT INTO item VALUES('BR0005','無臭にんにく・30日分',2800 ,99990); 
INSERT INTO item VALUES('BR0006','無臭にんにく・90日分',7400 ,100000); 
INSERT INTO item VALUES('BR0007','健康黒ゴマ・10日分',500 ,100000); 
INSERT INTO item VALUES('BR0008','健康黒ゴマ・30日分',1300 ,99990); 
INSERT INTO item VALUES('BR0009','健康黒ゴマ・90日分',3500 ,100000); 
INSERT INTO item VALUES('BR0010','黒ゴマセサミン・10日分',600 ,100000); 
INSERT INTO item VALUES('BR0011','黒ゴマセサミン・30日分',1500 ,99990); 
INSERT INTO item VALUES('BR0012','黒ゴマセサミン・90日分',4000 ,100000);
INSERT INTO item VALUES('CR0001','食べる納豆キナーゼ・10日分',600 ,99980); 
INSERT INTO item VALUES('CR0002','食べる納豆キナーゼ・30日分',1600 ,100000); 
INSERT INTO item VALUES('CR0003','食べる納豆キナーゼ・90日分',4500 ,100000);
INSERT INTO item VALUES('DR0001','雑穀プラス・10食分',500 ,100000); 
INSERT INTO item VALUES('DR0002','雑穀プラス・30食分',1300 ,100000); 
INSERT INTO item VALUES('DR0003','雑穀プラス・90食分',3500 ,100000); 
INSERT INTO item VALUES('DR0004','五穀米・10食分',1000 ,100000); 
INSERT INTO item VALUES('DR0005','五穀米・30食分',2800 ,100000); 
INSERT INTO item VALUES('DR0006','五穀米・90食分',8500 ,100000); 
INSERT INTO item VALUES('DR0007','十穀米・10食分',1200 ,100000); 
INSERT INTO item VALUES('DR0008','十穀米・30食分',3400 ,100000); 
INSERT INTO item VALUES('DR0009','十穀米・90食分',9500 ,100000); 
INSERT INTO item VALUES('DR0010','健康発芽玄米・10食分',1000 ,100000); 
INSERT INTO item VALUES('DR0011','健康発芽玄米・30食分',2800 ,100000); 
INSERT INTO item VALUES('DR0012','健康発芽玄米・90食分',8500 ,100000); 
INSERT INTO item VALUES('DR0013','健康黒酢（200ml）',350 ,100000); 
INSERT INTO item VALUES('DR0014','健康黒酢（1ｌ）',900 ,100000); 
INSERT INTO item VALUES('DR0015','健康黒酢（200ml）x12本',3500 ,100000); 
INSERT INTO item VALUES('DR0016','健康黒酢（1ｌ）x12本',9000 ,100000);
INSERT INTO item VALUES('ER0001','乳酸菌飲料ジョイ・6本パック',280 ,100000); 
INSERT INTO item VALUES('ER0002','乳酸菌飲料ジョイ・12本パック',500 ,100000); 
INSERT INTO item VALUES('ER0003','乳酸菌プラス・24袋パック',2200 ,100000); 
INSERT INTO item VALUES('ER0004','乳酸菌プラス・36袋パック',3000 ,100000); 
INSERT INTO item VALUES('ER0005','乳酸菌プラス・36袋パック',5000 ,100000); 
INSERT INTO item VALUES('ER0006','健康青汁・24袋パック',2200 ,100000); 
INSERT INTO item VALUES('ER0007','健康青汁・36袋パック',3000 ,100000); 
INSERT INTO item VALUES('ER0008','健康青汁・60袋パック',5000 ,100000);
INSERT INTO item VALUES('FR0001','マルチビタミン&ミネラル・10日分',1200 ,99990); 
INSERT INTO item VALUES('FR0002','マルチビタミン&ミネラル・30日分',3500 ,100000); 
INSERT INTO item VALUES('FR0003','マルチビタミン&ミネラル・120日分',12000 ,100000); 
INSERT INTO item VALUES('FR0004','マルチビタミンforMen・10日分',1200 ,100000); 
INSERT INTO item VALUES('FR0005','マルチビタミンforMen・30日分',3500 ,100000); 
INSERT INTO item VALUES('FR0006','マルチビタミンforMen・120日分',12000 ,100000); 
INSERT INTO item VALUES('FR0007','マルチビタミンforWomen・10日分',1200 ,100000); 
INSERT INTO item VALUES('FR0008','マルチビタミンforWomen・30日分',3500 ,100000); 
INSERT INTO item VALUES('FR0009','マルチビタミンforWomen・120日分',12000 ,100000); 
INSERT INTO item VALUES('FR0010','ビタミン13・10日分',1000 ,100000); 
INSERT INTO item VALUES('FR0011','ビタミン13・30日分',3500 ,100000); 
INSERT INTO item VALUES('FR0012','ビタミン13・120日分',10000 ,100000); 
INSERT INTO item VALUES('FR0013','ビタミンBB・10日分',900 ,100000); 
INSERT INTO item VALUES('FR0014','ビタミンBB・30日分',2500 ,100000); 
INSERT INTO item VALUES('FR0015','ビタミンBB・120日分',9000 ,100000); 
INSERT INTO item VALUES('FR0016','ビタミンC・10日分',800 ,100000); 
INSERT INTO item VALUES('FR0017','ビタミンC・30日分',2200 ,100000); 
INSERT INTO item VALUES('FR0018','ビタミンC・120日分',8000 ,100000); 
INSERT INTO item VALUES('FR0019','天然ビタミンＥ・10日分',900 ,100000); 
INSERT INTO item VALUES('FR0020','天然ビタミンＥ・30日分',2500 ,100000); 
INSERT INTO item VALUES('FR0021','天然ビタミンＥ・120日分',9000 ,100000); 
INSERT INTO item VALUES('FR0022','紫蘇・10日分',300 ,100000); 
INSERT INTO item VALUES('FR0023','紫蘇・30日分',800 ,100000); 
INSERT INTO item VALUES('FR0024','紫蘇・120日分',3000 ,100000); 
INSERT INTO item VALUES('FR0025','天然アミノ・10日分',350 ,100000); 
INSERT INTO item VALUES('FR0026','天然アミノ・30日分',1200 ,100000); 
INSERT INTO item VALUES('FR0027','天然アミノ・120日分',4000 ,100000); 
INSERT INTO item VALUES('FR0028','甜茶･10日分',300 ,100000); 
INSERT INTO item VALUES('FR0029','甜茶･30日分',800 ,100000); 
INSERT INTO item VALUES('FR0030','甜茶･120日分',3000 ,100000); 
INSERT INTO item VALUES('FR0031','天然田七人参・10日分',300 ,100000); 
INSERT INTO item VALUES('FR0032','天然田七人参・30日分',800 ,100000); 
INSERT INTO item VALUES('FR0033','天然田七人参・30日分',3000 ,100000);
INSERT INTO item VALUES('GR0001','健康十穀の粥・1食',120 ,99990); 
INSERT INTO item VALUES('GR0002','健康十穀の粥・10食パック',1000 ,100000); 
INSERT INTO item VALUES('GR0003','健康十穀の粥・30食パック',2800 ,100000); 
INSERT INTO item VALUES('GR0004','健康十穀の粥・90食パック',8000 ,99990); 
INSERT INTO item VALUES('GR0005','健康十穀の粥(カレー)・1食',120 ,99990); 
INSERT INTO item VALUES('GR0006','健康十穀の粥(カレー）・10食パック',1000 ,100000); 
INSERT INTO item VALUES('GR0007','健康十穀の粥(カレー)・30食パック',2800 ,100000); 
INSERT INTO item VALUES('GR0008','健康十穀の粥(カレー)・90食パック',8000 ,99990);
INSERT INTO item VALUES('HR0001','健康低反発まくらS',12000 ,100000); 
INSERT INTO item VALUES('HR0002','健康低反発まくらM',12500 ,100000); 
INSERT INTO item VALUES('HR0003','健康低反発まくらL',13000 ,100000);
INSERT INTO item VALUES('IR0001','健康オーダーまくらS',17000 ,100000); 
INSERT INTO item VALUES('IR0002','健康オーダーまくらM',17500 ,100000); 
INSERT INTO item VALUES('IR0003','健康オーダーまくらL',18000 ,100000);
INSERT INTO item VALUES('JR0001','男性用育毛トニック',6500 ,99990); 
INSERT INTO item VALUES('JR0002','女性用育毛トニック',6500 ,99990); 
INSERT INTO item VALUES('JR0003','育毛シャンプー',2000 ,99990); 
INSERT INTO item VALUES('JR0004','育毛コンディショナー',2200 ,99990);


-- /*================================================================*/
-- /*  受注（orders）テーブル データ挿入                             */
-- /*================================================================*/

INSERT INTO orders VALUES ('000001','RA0001','R20001',800,1,'2016-11-10','2016-11-9');
INSERT INTO orders VALUES ('000002','RA0015','R20002',12000,1,'2016-12-8','2016-12-7');
INSERT INTO orders VALUES ('000003','RA0015','R20001',6000,1,'2016-12-1','2016-12-1');
INSERT INTO orders VALUES ('000004','RA0001','R20003',13200,2,'2016-12-10','2016-12-9');
INSERT INTO orders VALUES ('000005','RA0014','R20001',172000,4,'2017-1-5','2017-1-5');
INSERT INTO orders VALUES ('000006','RA0003','R20003',86000,4,'2017-2-10','2017-2-10');
INSERT INTO orders VALUES ('000007','RA0001','R20001',18000,2,'2017-2-15','2017-2-15');
INSERT INTO orders VALUES ('000008','RA0003','R20002',174400,5,'2017-3-20','2017-3-20');


-- /*================================================================*/
-- /*  受注明細（order_details）テーブル データ挿入                  */
-- /*================================================================*/

INSERT INTO order_details VALUES('000001','AR0001',10,800);
INSERT INTO order_details VALUES('000002','BR0001',10,12000);
INSERT INTO order_details VALUES('000003','CR0001',10,6000);
INSERT INTO order_details VALUES('000004','AR0001',15,1200);
INSERT INTO order_details VALUES('000004','BR0001',10,12000);
INSERT INTO order_details VALUES('000005','JR0001',10,65000);
INSERT INTO order_details VALUES('000005','JR0002',10,65000);
INSERT INTO order_details VALUES('000005','JR0003',10,20000);
INSERT INTO order_details VALUES('000005','JR0004',10,22000);
INSERT INTO order_details VALUES('000006','BR0002',10,30000);
INSERT INTO order_details VALUES('000006','BR0005',10,28000);
INSERT INTO order_details VALUES('000006','BR0008',10,13000);
INSERT INTO order_details VALUES('000006','BR0011',10,15000);
INSERT INTO order_details VALUES('000007','BR0001',10,12000);
INSERT INTO order_details VALUES('000007','CR0001',10,6000);
INSERT INTO order_details VALUES('000008','FR0001',10,12000);
INSERT INTO order_details VALUES('000008','GR0001',10,1200);
INSERT INTO order_details VALUES('000008','GR0004',10,80000);
INSERT INTO order_details VALUES('000008','GR0005',10,1200);
INSERT INTO order_details VALUES('000008','GR0008',10,80000);


COMMIT;

