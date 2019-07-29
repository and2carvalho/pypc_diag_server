from flask_app import db

class Ocor_bios(db.Model):
    __tablename__ = 'tab_ocorBios'
    ocor_id = db.Column(db.String(500), primary_key=True)
    id_maq = db.Column(db.String(255), index=True)
    nome_processador = db.Column(db.String(255), index=True)
    qtd_processador = db.Column(db.Integer, index=True)
    memo_total = db.Column(db.Float)
    memo_disp = db.Column(db.Float)
    nome_maq = db.Column(db.String(255),index=True)
    data_ocor = db.Column(db.DateTime, index=True)
    hds = db.relationship('Ocor_hd',backref='hd')
    processos = db.relationship('Ocor_proc',backref='processos')
    instalados = db.relationship('Ocor_insta',backref='instalados')
    impressoras = db.relationship('Ocor_imp',backref='impressoras')
    teste_ping = db.relationship('Ocor_ping',backref='ping')
    teste_net = db.relationship('Ocor_net',backref='net')
    info_user = db.relationship('Ocor_user',backref='usuario')

    def as_dict(self):
        return {'ocor_id':self.ocor_id,
                'id_maq':self.id_maq,
                'nome_processador':self.nome_processador,
                'qtd_processador':self.qtd_processador,
                'memo_total':self.memo_total,
                'memo_disp':self.memo_disp,
                'nome_maq':self.nome_maq,
                'data_ocor':self.data_ocor}
    
class Ocor_hd(db.Model):
    __tablename__ = 'tab_ocorHd'
    reg_id = db.Column(db.Integer, primary_key=True)
    ocor_id = db.Column(db.String(500), db.ForeignKey('tab_ocorBios.ocor_id'))
    hd_nome = db.Column(db.String(255))
    hd_tamanho = db.Column(db.Float)
    hd_livre = db.Column(db.Float)

class Ocor_proc(db.Model):
    __tablename__ = 'tab_ocorProc'
    reg_id = db.Column(db.Integer, primary_key=True)
    ocor_id = db.Column(db.String(500), db.ForeignKey('tab_ocorBios.ocor_id'))
    proc_nome = db.Column(db.String(255), index=True)
    proc_pid = db.Column(db.Integer)
    proc_memo = db.Column(db.Float)
    proc_cpu = db.Column(db.Float)
    proc_usuario = db.Column(db.String(255))

class Ocor_insta(db.Model):
    __tablename__ = 'tab_ocorInsta'
    reg_id = db.Column(db.Integer, primary_key=True)
    ocor_id = db.Column(db.String(500), db.ForeignKey('tab_ocorBios.ocor_id'))
    prog_nome = db.Column(db.String(255), index=True)
    prog_vers = db.Column(db.String(255))

class Ocor_imp(db.Model):
    __tablename__ = 'tab_ocorImp'
    reg_id = db.Column(db.Integer, primary_key=True)
    ocor_id = db.Column(db.String(500), db.ForeignKey('tab_ocorBios.ocor_id'))
    imp_nome = db.Column(db.String(255))
    imp_porta = db.Column(db.String(255))
    imp_jobs = db.Column(db.Integer)
    imp_status = db.Column(db.Integer)

class Ocor_ping(db.Model):
    __tablename__ = 'tab_ocorPing'
    reg_id = db.Column(db.Integer, primary_key=True)
    ocor_id = db.Column(db.String(500), db.ForeignKey('tab_ocorBios.ocor_id'))
    sofstore_medPing = db.Column(db.Float)
    sofstore_passed = db.Column(db.Integer)
    sofstore_failed = db.Column(db.Integer)
    google_medPing = db.Column(db.Float)
    google_passed = db.Column(db.Integer)
    google_failed = db.Column(db.Integer)

class Ocor_net(db.Model):
    __tablename__ = 'tab_ocorNet'
    reg_id = db.Column(db.Integer, primary_key=True)
    ocor_id = db.Column(db.String(500), db.ForeignKey('tab_ocorBios.ocor_id'))
    download = db.Column(db.Float)
    upload = db.Column(db.Float)
    ping = db.Column(db.Float)
    prov_net = db.Column(db.String(255))

class Ocor_user(db.Model):
    __tablename__ = 'tab_ocorUser'
    reg_id = db.Column(db.Integer, primary_key=True)
    ocor_id = db.Column(db.String(500), db.ForeignKey('tab_ocorBios.ocor_id'))
    user = db.Column(db.String(255))
    loja = db.Column(db.String(255))
    
    
    
    
