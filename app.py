from flask import Flask, session, redirect, request, render_template, jsonify
import pymysql
from ulit import con_db, timesf

app = Flask(__name__)

app.secret_key = '1234qwerasdfzxcvtrewgfdsa'


@app.route('/')
def index():
    return redirect('/user/user_login')


@app.route('/admin')
def admin():
    return redirect('/admin/admin_login')


@app.route('/<ty>/<page>')
def mb(ty, page):
    """
    模板控制
    :param page:
    :return:
    """
    con = con_db()
    cu = con.cursor(pymysql.cursors.DictCursor)
    if ty == 'user':
        if page == 'user_login':
            # 用户登录
            return render_template('user_login.html')
        elif page == 'user_index':
            # 用户首页
            cu.execute("select departureCityName from data group by departureCityName")
            departureCityNames = cu.fetchall()
            cu.execute("select arrivalCityName from data group by arrivalCityName")
            arrivalCityNames = cu.fetchall()
            return render_template('user_index.html', **{'departureCityNames': departureCityNames,
                                                         'arrivalCityNames': arrivalCityNames})
        elif page == 'user_order':
            user = session.get('user')
            cu.execute("select * from `order` o left join data d on o.did=d.id where user=%s", (user,))
            data = cu.fetchall()

            timesf(data)
            print(data)
            return render_template('user_order.html', **{'data': data})

    else:
        if page == 'admin_login':
            # 管理员登录
            return render_template('admin_login.html')
        elif page == 'admin_index':
            # 管理用户管理
            return render_template('admin_index.html')


@app.route('/uapi/', methods=['POST'])
def uapi():
    """
    接口
    :return:
    """
    code = request.form.get('code')
    print(code)
    user = session.get('user')
    con = con_db()
    cu = con.cursor(pymysql.cursors.DictCursor)
    if code == 'user_reg':
        # 用户注册
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        cu.execute("select id from users where user=%s", (user,))
        if cu.fetchall():
            return jsonify({'code': 1, 'msg': 'Пользователь уже существует！'}) # 用户已存在
        cu.execute("insert into users(user,pwd) values (%s,%s)", (user, pwd))
        con.commit()
        return jsonify({'code': 0, 'msg': 'Успешно зарегистрировались!'}) # 注册成功
    elif code == 'user_login':
        # 用户登录
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        cu.execute("select id from users where user=%s and pwd=%s", (user, pwd))
        data = cu.fetchall()
        if data:
            session['user'] = user
            return jsonify({'code': 0, 'msg': 'Успешно входа!'})
        return jsonify({'code': 1, 'msg': 'Ошибка входа!'})
    elif code == 'admin_login':
        # 管理登录
        user = request.form.get('user')
        pwd = request.form.get('pwd')

        if user == 'admin' and pwd == 'admin':
            session['user'] = user
            return jsonify({'code': 0, 'msg': 'Успешно входа!'})
        return jsonify({'code': 1, 'msg': 'Ошибка входа!'})
    elif code == 'sel_data':
        # 处理选项
        ty = request.form.get('ty')
        if ty == 'departureCityName':
            # 选择始发
            departureCityName = request.form.get('departureCityName')
            cu.execute("select arrivalCityName from data where departureCityName=%s group by arrivalCityName",
                       (departureCityName,))
            data = cu.fetchall()
            return jsonify({'code': 0, 'data': data})
        elif ty == 'arrivalCityName':
            # 到达
            departureCityName = request.form.get('departureCityName')
            arrivalCityName = request.form.get('arrivalCityName')
            cu.execute(
                "select flightNo from data where departureCityName=%s and arrivalCityName=%s group by flightNo",
                (departureCityName, arrivalCityName))
            data = cu.fetchall()
            return jsonify({'code': 0, 'data': data})

    elif code == 'admin_users':
        # 用户管理
        user_kw = request.form.get('user_kw')
        page = int(request.form.get('page')) - 1
        limit = int(request.form.get('limit'))
        sql = 'select * from users where 1=1 '
        sqlct = 'select count(*)ct from users where 1=1 '
        if user_kw:
            sql += f' and user like "%{user_kw}%"'
            sqlct += f' and user like "%{user_kw}%"'

        sql += f' limit {page * limit},{limit}'

        cu.execute(sqlct)
        count = cu.fetchall()[0].get('ct')
        cu.execute(sql)
        data = cu.fetchall()
        return jsonify({'code': 0, 'msg': 'ok', 'data': data, 'count': count})

    elif code == 'user_del':
        uid = request.form.get('uid')
        cu.execute("delete from users where id=%s", (uid,))
        con.commit()
        return jsonify({'code': 0, 'msg': 'Успешно удален!'}) # 删除成功
    elif code == 'user_eidt':
        uid = request.form.get('uid')
        pwd = request.form.get('pwd')
        cu.execute("update users set pwd=%s where id=%s", (pwd, uid,))
        con.commit()
        return jsonify({'code': 0, 'msg': 'Успешно изменено！'}) # 修改成功
    elif code == 'cxhangb':
        # 查询航班次
        sdate = request.form.get('sdate')
        departureCityName = request.form.get('departureCityName')
        arrivalCityName = request.form.get('arrivalCityName')
        cu.execute("select * from data where departureCityName=%s and arrivalCityName=%s",
                   (departureCityName, arrivalCityName))
        data = cu.fetchall()
        return jsonify({'code': 0, 'data': data})
    elif code == 'goumai':
        # 购买
        did = request.form.get('did')
        sdate = request.form.get('sdate')
        cu.execute("insert into `order`(did,user,sdate)values (%s,%s,%s)", (did, user, sdate))
        con.commit()
        return jsonify({'code': 0, 'msg': 'Успешная покупка!'}) # 购买成功
    elif code == 'tuipiao':
        # 退票
        oid = request.form.get('oid')
        cu.execute("delete from `order` where id=%s", (oid,))
        con.commit()
        return jsonify({'code': 0, 'msg': 'Успешный возврат!'}) # 退票成功
    elif code == 'gaiqian':
        # 改签
        oid = request.form.get('oid')
        sdate = request.form.get('sdate')
        cu.execute("update `order` set sdate=%s where id=%s", (sdate, oid))
        con.commit()
        return jsonify({'code': 0, 'msg': 'Успешно изменено!'}) # 改签成功


if __name__ == '__main__':
    app.run()
