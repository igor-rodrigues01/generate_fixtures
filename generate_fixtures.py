#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import sys
import os
import json

from collections import defaultdict
"""
formatar campos date e datetime

teste:
python3 generate_fixtures.py --model usermanager.Orgao --filename ../be_catalogo/sqls/fix_teste3 --fields -name Orgao Teste ~pk 1 -email abc@abc.com -contato Maria -cep 1112223 -cnpj 121212223123 -telefone 23433234 -esfera_id 1 -status_id 1 -date_creation 2018-01-01  --new -name Orgao Teste ~pk 1 -email abc@abc.com -contato Maria -cep 1112223 -cnpj 121212223123 -telefone 23433234 -esfera_id 1 -status_id 1 -date_creation 2018-01-01 
"""
class Utils:

    performed_action_controll_start_comma = None

    def doc_tutorial(self):
        """
        Documentacao para o usuario
        """
        print("--model    "\
            "= Modelo da aplicação (appDjando.ModelName)."
        )
        print("--filename = Nome do arquivo com o path onde deseja salvar"\
            " (todos os arquivos serão salvos com a extensão .json)."
        )
        print("--fields   = Nome dos campos do modelo (Crie o nome"\
            " de cada campo passando o parâmetro com um trasso atrás (-name)."
        )
        print("--new      = Novo registro para este modelo"\
            " (Após --new repita o processo do parâmetro --f)."
        )
        print("~pk        = Em cada registro deve existir "\
            "uma chave (com qualquer nome) e seu nome deve "\
            "estar após o símbolo (~pk).\n\t   É obrigatório que"\
            " a chave primária contenha um til antes"\
            " de seu nome (~pkname)."
        )
        print('\n# Caso precise utilizar valores com espaços'\
            ' utilize aspas duplas (--param "value with space").'
        )
        print("# Para cada novo registro utilize o parâmetro --new."
        )
        print("# Campos do tipo date ou datetime deverão estar"\
            " no seguinte formato (date - AAAA-MM-DD | datetime"\
            " AAAA-MM-DD_HH:MM:S)."
        )
        # Example to user
        print('\n\tpython generate_fixtures.py --model appDjando.modelTeste'\
            ' --filename fix --f ~pk 1 -name '\
            '"josé silva" -date_creation 2018-01-01_12:40:00 \n\t\t\t\t\t--new'\
            ' ~pk 2 -name joao -date_creation 2018-01-02_16:40:00 \n'
        )

    def get_filename(self,lambda_get_value):
        """
        Obtendo o nome do arquivo
        """
        try:
           return lambda_get_value('--filename')
        except Exception:
            return 'fixture'

    def get_register_quantity(self,param):
        """
        Esta funca e necessaria para que o range (da funcao write_jsonfile) alcance a
        quantidade de registros apos o paramentro --new
        """
        if sys.argv.count(param) > 0:
            return sys.argv.count(param) + 1
        else:
            return 0

    def adapt_pk_in_data_type(self,pk):
        """
        Funcao que adapta a primary key conforme seu tipo de dado
        """
        if pk.isdigit():
            return pk
        else:
            return '"'+pk+'"'

    def controll_start_comma(self,is_new_file):
        """ 
        Funcao que adiciona e remove virgulas no registro anterior a um novo registro
        """
        comma = None

        if not is_new_file and self.performed_action_controll_start_comma == False:
            self.performed_action_controll_start_comma = True
            comma = ','
        else:
            comma = ''

        return comma 

    def controll_end_comma(self,range_of_iteration,current_index):
        """
        Funcao que adiciona e remove virgulas no final de cada registro
        """
        comma = None

        if range_of_iteration > 0:
            if current_index == range_of_iteration - 1:
                comma = ''
            else:
                comma = ',' 
        else:
            comma = ''

        return comma

    def get_sub_register(self,fields_from_argv_and_values,register_quantity):
        """
        Funcao que tranformarma a lista de fiels (--fields) em sublistas dividida por registro
        """
        register_list                = []
        current_register_list        = []
        current_register_number      = 1
        params_quantity_after_fields = len(fields_from_argv_and_values)

        for index in range(params_quantity_after_fields):
            if fields_from_argv_and_values[index] != '--new':
                current_register_list.append(fields_from_argv_and_values[index])
            
            if register_quantity == current_register_number and index == params_quantity_after_fields - 1:
                register_list.append(current_register_list)
                break

            if fields_from_argv_and_values[index] == '--new':
                current_register_number += 1
                register_list.append(current_register_list)
                current_register_list = []
                continue

        return register_list

    def error_message_and_exit(self,msg):
        """
        Funcao que imprime uma mensagem de erro e finaliza o script
        """
        print('\n{}\n'.format(msg))
        sys.exit()

class StatementError:

    utils = None
    
    def __init__(self):
        self.utils = Utils()

    def check_value_model(self):
        """
        Funcao que verifica o valor do parametro --model verificando se existe um ponto
        (.) nop meio do valor para identificar que este valor possuir um djangoApp.ModelName
        """
        if sys.argv[2].find('.',1,-1) == -1:
            self.utils.error_message_and_exit('O valor de --model está incompleto.'\
                ' Utilize a seguinte sintaxe (--model djangoapp.ModelName)'
            )

    def check_exists_pk(self):
        """
        Funcao que verifica se a pk existe e mostra em qual registro esta sem um pk
        """
        register_quantity   = 0
        register_list       = []
        register_without_pk = []
        list_as_str         = None

        register_quantity           = self.utils.get_register_quantity('--new')
        fields_from_argv_and_values = sys.argv[6:]

        def get_register_without_pk(register,only_one_register,register_list=None):
            """
            Funcao que obtem o numero do resgitro que esta sem um pk
            """
            register_without_pk = []
            pk_quantity         = 0
            is_not_pk           = 0

            for item in register:
                if item.find('~',0,1) is not -1:
                    pk_quantity += 1
                else:
                    is_not_pk += 1

            if only_one_register:
                if is_not_pk == len(register):
                    register_without_pk.append(1)
            else:
                if is_not_pk == len(register):
                    register_without_pk.append(
                        register_list.index(register) + 1
                    )
            return register_without_pk  

        if register_quantity > 0:
            register_list = self.utils.get_sub_register(
                fields_from_argv_and_values,register_quantity
            )
            
            for register in register_list:
                register_without_pk = get_register_without_pk(
                    register,register_list=register_list,only_one_register=False
                )

        else:
            for param in fields_from_argv_and_values:
                register_without_pk = get_register_without_pk(
                    fields_from_argv_and_values,only_one_register=True
                )

        if register_without_pk:
            list_as_str = 'º, '.join(str(item) for item in register_without_pk)

            self.utils.error_message_and_exit(
                'Está faltando uma chave primária (~pk)'\
                ' no {}º registro.'.format(list_as_str)
            )

    def check_fields_param(self):
        """
        Funcao que verifica se os paramentros em posicoes impares possuem uma simbologia (-/~)
        para identificar que sao campos
        """
        register_quantity           = 0
        register_list               = []
        fields_from_argv_and_values = []

        register_quantity = self.utils.get_register_quantity('--new')
        fields_from_argv_and_values = sys.argv[6:]

        def loop_in_list_checking_params(register):
            """
            Funcao que realiza um loop em um registro verificando se os itens
            impares possuem um simbologia (-/~)
            """
            for index in range(len(register)):
                # esta linha de codigo (register[index].find('~',0,1) is not -1 or register[index].find('-',0,1) is not -1)
                # verifica se o item possui a simbologia (-,~) no inicio 
                if index % 2 == 0 and not (register[index].find('~',0,1) is not -1 or register[index].find('-',0,1) is not -1):
                    self.utils.error_message_and_exit(
                        'Nome de campos não definido ou está sem a simbologia,'\
                        ' verifique os espaçamemento de alguns valores.'\
                        ' Utilize a seguinte sintaxe para nomear um campo (-name).'
                    )

        if register_quantity > 0:
            register_list = self.utils.get_sub_register(
                fields_from_argv_and_values,register_quantity
            )
            for register in register_list:
                loop_in_list_checking_params(register)
        else:
            loop_in_list_checking_params(fields_from_argv_and_values) 

    def check_values_fields_param(self):
        """
        Funcao que verifca se a quatidade de parametros apos --field sao pares
        pois devem ser em pares (-key value)
        """
        register_quantity           = 0
        register_list               = []
        fields_from_argv_and_values = []

        register_quantity = self.utils.get_register_quantity('--new')
        fields_from_argv_and_values = sys.argv[6:]
        
        def check_pairs(register):
            """
            funcao que verifica se os valores do registros estao em pares (-key/value)
            """
            if len(register) % 2 != 0:
                self.utils.error_message_and_exit(
                'Campos sem valores após --fields. Verifique os espaçamemento de alguns valores.'
            )

        if register_quantity > 0:
            register_list = self.utils.get_sub_register(
                fields_from_argv_and_values,register_quantity
            )
            for register in register_list:
                check_pairs(register)
        else:
            check_pairs(fields_from_argv_and_values)

    def check_values_primary_params(self):
        """
        Funcao que verifica se os parametros primarios 
        (parametros com dois trascos (--model/--filename)) estao na posicao correta
        """
        primary_params_from_argv = []

        primary_params_from_argv = sys.argv[1:5]
        if len(primary_params_from_argv) < 4:
            self.utils.error_message_and_exit(
                'Esta faltando valores ou parâmetros primários.'
            )

    def check_params_orders(self):
        """
        Funcao que verifica a ordem do parametros primarios
        """
        if sys.argv[1] != '--model':
            self.utils.error_message_and_exit(
                '--model está no lugar errado ou não existe.\n'\
                ' em seu lugar está {}.'.format(sys.argv[1])
            )
        elif sys.argv[3] != '--filename':
            self.utils.error_message_and_exit(
                '--filename estregister_quantityá no lugar errado ou não existe.'\
                '\n em seu lugar está {}.'.format(sys.argv[3])
            )
        elif sys.argv[5] != '--fields':
            self.utils.error_message_and_exit(
                '--fields está no lugar errado ou não existe.'\
                '\n em seu lugar está {}.'.format(sys.argv[5])
            )

    def errors_correction(self):
        """
        Funcao que executa as funcoes de tratamento de erro
        """
        self.check_values_fields_param()
        self.check_values_primary_params()
        self.check_params_orders()
        self.check_exists_pk()
        self.check_fields_param()
        self.check_value_model()

class Main:

    utils      = None
    stmt_errors = None

    def __init__(self):
        self.utils = Utils()
        self.stmt_errors = StatementError()
    
    def data_extracted(self):
        """
        Funcao que extrai e formata os dados deixando-os prontos para o processamento
        """
        get_value        = None
        dict_values      = {}
        fields_from_argv = []
        fields           = defaultdict(list)
        key              = None
        filename         = None
        pk               = defaultdict(list)
        controller       = 0
        pk_name          = None
        pk_value         = None
        param_as_list    = []

        # getting value of each parameter
        get_value        = lambda parameter:sys.argv[sys.argv.index(parameter) + 1]
        
        filename         = self.utils.get_filename(get_value)
        fields_from_argv = sys.argv[sys.argv.index('--fields') + 1:]

        """
        A variavel "controller" serve para controlar a iteracao para que a contagem esteja
        sempre em um indice que permita obter a chave dos argumentos 
        (onde, ao usar "fields_from_argv[controller]" sera retornado algum parametro chave 
        (parametros com um traco atras), passados pelo terminal.
        E sempre que for usado "fields_from_argv[controller + 1]"
        sera retornado o valor do parametro chave.
        """
        for param in fields_from_argv:
            if param == '--new':
                controller += 1
                continue
            else:
                if param.find('~',0,1) is not -1:
                    pk_name       = param.replace('~','')
                    pk_value      = fields_from_argv[controller + 1]
                    pk['pk_name'] = pk_name
                    pk['pk_value'].append(pk_value)

                if param.find('-',0,1) is not -1:
                    param_as_list = list(param)
                    param_as_list.pop(0)
                    key = ''.join(param_as_list)
                    fields[key].append(fields_from_argv[controller + 1])
                
            controller += 1
        
        dict_values = {
            'filename': filename,
            'model':get_value('--model'),
            'register_quantity':self.utils.get_register_quantity('--new'),
            'pk':pk,
            'fields':fields
        }
        return dict_values
    
    def open_or_create_file(self,file_path):
        """
        Funcao que verificando se arquivo existe, se nao existir sera criado um novo arquivo
        """
        json_file   = None
        is_new_file = False
        try:
            if os.path.exists(file_path):
                json_file = open(file_path,'r+')
            else:
                json_file = open(file_path,'w+')
                json_file.write('[\n')
                is_new_file = True
        except Exception as ex:
            self.utils.error_message_and_exit(
                'Path inválido. Adicione um path válido para o parâmetro --filename'\
                ' (--filename path/valid/file).'
            ) 

        return (json_file,is_new_file)

    def prepare_file_to_update(self,json_file):
        """
        Funcao que prepara o arquivo para atualizacao removendo o ultimo colchete conteudo antigo 
        """
        # Removendo colchetes para adicionar novos registros no mesmo arquivo
        lines = json_file.readlines()
        # removendo o \n para adicionar a nova virgula(controll_start_comma)
        lines[-2] = lines[-2].replace('\n','') 
        #removendo o colchete final
        lines.pop() 
        json_file = open(json_file.name,'w')
        json_file.writelines(lines)
        return json_file

    def create_content_main(self,data_extracted,is_new_file,current_index=0):
        """
        Funcao que formata o conteudo principal para ser escrito no arquivo
        """
        dict_to_json_dumps          = {}
        content                     = None
        fields_and_values_from_argv = data_extracted['fields']
        pk                          = data_extracted['pk']
        register_quantity           = data_extracted['register_quantity']

        for key,value in fields_and_values_from_argv.items():
            dict_to_json_dumps[key] = value[0]
                
        # Conteudo que esta no sys.argv
        content = '{start_comma}'\
                   '\t\n\t{open_key}\n'\
                   '\n\t\t"model":"%s",'\
                   '\n\t\t"%s":{pk_value},'\
                   '\n\t\t"fields":%s\n'\
                   '\n\t{close_key}'\
                   '{end_comma}'.format(
                        open_key='{',
                        close_key='}',
                        start_comma=self.utils.controll_start_comma(is_new_file),
                        end_comma=self.utils.controll_end_comma(
                            register_quantity,
                            current_index
                        ), 
                        pk_value=self.utils.adapt_pk_in_data_type(
                            str(pk['pk_value'][current_index])
                    )
        ) 
        content = content % (
                        data_extracted['model'],
                        pk['pk_name'],
                        json.dumps(dict_to_json_dumps)
        )
        return content

    def write_jsonfile(self,data_extracted):
        """
        Funcao que escreve o conteudo principal no arquivo
        """
        is_new_file                 = False
        json_file                   = None
        
        file_path                   = '{}.json'.format(data_extracted['filename'])
        json_file,is_new_file       = self.open_or_create_file(file_path)
        register_quantity           = data_extracted['register_quantity']
        
        if not is_new_file:
            self.utils.performed_action_controll_start_comma = False
            json_file = self.prepare_file_to_update(json_file)        
        
        if register_quantity > 0:
            for current_index in range(register_quantity):
                json_file.write(
                    self.create_content_main(
                        data_extracted,is_new_file,current_index
                    )
                )
        else:
            json_file.write(
                    self.create_content_main(
                        data_extracted,is_new_file
                    )
                )

        json_file.write('\n]\n')
        json_file.close()

        if is_new_file:
            print('\nArquivo {} criado com sucesso!\n'.format(file_path))
        else:
            print('\nArquivo {} atualizado com sucesso!\n'.format(file_path))

    def main(self):
        if len(sys.argv) == 1:
            self.utils.doc_tutorial()
        else:
            self.stmt_errors.errors_correction()
            self.write_jsonfile(
                self.data_extracted()
            )
  

if __name__ == '__main__':
    Main().main()