INSERT INTO transaction_types (type) VALUES
  ('INCOME'),
  ('EXPENSES'),
  ('TRANSFER')
ON CONFLICT DO NOTHING;

INSERT INTO categories (name) VALUES
  ('comida'),
  ('besteira'),
  ('estudo'),
  ('férias'),
  ('transporte'),
  ('moradia'),
  ('saúde'),
  ('lazer'),
  ('contas'),
  ('investimento'),
  ('presente'),
  ('outros')
ON CONFLICT DO NOTHING;

INSERT INTO transactions (amount, type, category_id, description, payment_method, occurred_at, source_text) VALUES
  (3500.00, 1, 12, 'Salário mensal', 'PIX', '2026-04-01 09:00:00-03', 'Recebi meu salário de abril'),
  (120.50, 2, 1, 'Supermercado', 'Cartão de Crédito', '2026-04-02 18:30:00-03', 'Compra de alimentos no mercado'),
  (45.00, 2, 4, 'Cinema', 'Débito', '2026-04-03 20:00:00-03', 'Ingresso de cinema'),
  (89.90, 2, 3, 'Curso online', 'Cartão de Crédito', '2026-04-04 14:00:00-03', 'Assinatura de plataforma de estudos'),
  (220.00, 2, 5, 'Combustível', 'PIX', '2026-04-05 08:15:00-03', 'Abastecimento do carro'),
  (1500.00, 2, 6, 'Aluguel', 'Transferência', '2026-04-05 10:00:00-03', 'Pagamento do aluguel'),
  (75.30, 2, 7, 'Farmácia', 'Débito', '2026-04-06 12:45:00-03', 'Medicamentos e itens de higiene'),
  (200.00, 2, 8, 'Restaurante', 'Cartão de Crédito', '2026-04-07 21:00:00-03', 'Jantar com amigos'),
  (350.00, 2, 9, 'Conta de energia', 'PIX', '2026-04-08 11:20:00-03', 'Pagamento da conta de luz'),
  (500.00, 1, 10, 'Rendimento de investimento', 'Transferência', '2026-04-09 16:00:00-03', 'Lucro de aplicação financeira'),
  (60.00, 2, 1, 'Delivery', 'Cartão de Crédito', '2026-04-10 19:30:00-03', 'Pedido de comida'),
  (35.00, 2, 2, 'Chocolate e snacks', 'Dinheiro', '2026-04-11 15:10:00-03', 'Compra de guloseimas'),
  (180.00, 2, 11, 'Presente de aniversário', 'PIX', '2026-04-12 13:00:00-03', 'Compra de presente'),
  (250.00, 3, 10, 'Transferência para investimentos', 'Transferência', '2026-04-13 09:30:00-03', 'Aporte em investimentos'),
  (90.00, 2, 5, 'Uber', 'Cartão de Crédito', '2026-04-14 22:15:00-03', 'Corridas de aplicativo'),
  (420.00, 2, 9, 'Internet e telefone', 'Débito Automático', '2026-04-15 08:00:00-03', 'Pagamento de serviços de telecomunicação'),
  (130.00, 2, 7, 'Consulta médica', 'PIX', '2026-04-16 10:30:00-03', 'Consulta clínica geral'),
  (800.00, 1, 12, 'Freelance', 'PIX', '2026-04-18 17:00:00-03', 'Pagamento por projeto freelancer'),
  (250.00, 2, 8, 'Passeio de fim de semana', 'Cartão de Crédito', '2026-04-20 14:00:00-03', 'Atividades de lazer'),
  (110.00, 2, 1, 'Almoço em restaurante', 'Débito', '2026-04-22 12:30:00-03', 'Almoço de negócios');

INSERT INTO notes (content, source_text, items, concluded, recorded_at, concluded_at) VALUES
  ('Comprar mantimentos da semana', 'Lista mental antes de sair', ARRAY['arroz','feijão','leite','ovos'], FALSE, '2026-04-01 09:00:00-03', NULL),
  ('Finalizar relatório mensal', 'Demanda do trabalho', ARRAY['dados','gráficos','revisão'], TRUE, '2026-04-01 10:00:00-03', '2026-04-02 15:00:00-03'),
  ('Treino na academia', 'Planejamento diário', ARRAY['peito','tríceps','cardio'], FALSE, '2026-04-02 07:00:00-03', NULL),
  ('Estudar SQL', 'Meta de aprendizado', ARRAY['joins','indexes','CTE'], FALSE, '2026-04-02 20:00:00-03', NULL),
  ('Pagar contas do mês', 'Lembrete financeiro', ARRAY['luz','água','internet'], TRUE, '2026-04-03 08:00:00-03', '2026-04-03 09:00:00-03'),
  ('Organizar workspace', 'Produtividade', ARRAY['limpeza','cabos','arquivos'], TRUE, '2026-04-03 18:00:00-03', '2026-04-03 19:00:00-03'),
  ('Planejar viagem', 'Conversa com amigos', ARRAY['passagens','hotel','roteiro'], FALSE, '2026-04-04 12:00:00-03', NULL),
  ('Ler livro técnico', 'Estudo contínuo', ARRAY['cap1','cap2','anotações'], FALSE, '2026-04-04 22:00:00-03', NULL),
  ('Atualizar currículo', 'Busca de oportunidades', ARRAY['experiências','skills'], TRUE, '2026-04-05 14:00:00-03', '2026-04-05 16:00:00-03'),
  ('Reunião com equipe', 'Sprint semanal', ARRAY['status','bloqueios'], TRUE, '2026-04-06 10:00:00-03', '2026-04-06 11:00:00-03'),
  ('Backup dos arquivos', 'Segurança de dados', ARRAY['docs','fotos'], TRUE, '2026-04-06 23:00:00-03', '2026-04-06 23:30:00-03'),
  ('Estudar inglês', 'Rotina diária', ARRAY['listening','speaking'], FALSE, '2026-04-07 19:00:00-03', NULL),
  ('Ir ao médico', 'Check-up anual', ARRAY['exames','consulta'], TRUE, '2026-04-08 09:00:00-03', '2026-04-08 10:30:00-03'),
  ('Planejar semana', 'Organização pessoal', ARRAY['tarefas','prioridades'], TRUE, '2026-04-09 08:00:00-03', '2026-04-09 08:45:00-03'),
  ('Limpar a casa', 'Rotina doméstica', ARRAY['quarto','sala','cozinha'], FALSE, '2026-04-10 11:00:00-03', NULL),
  ('Assistir curso online', 'Capacitação', ARRAY['aula1','aula2'], FALSE, '2026-04-10 21:00:00-03', NULL),
  ('Configurar projeto novo', 'Dev task', ARRAY['repo','env','db'], TRUE, '2026-04-11 15:00:00-03', '2026-04-11 18:00:00-03'),
  ('Responder emails', 'Trabalho', ARRAY['clientes','interno'], TRUE, '2026-04-12 09:30:00-03', '2026-04-12 10:15:00-03'),
  ('Caminhada no parque', 'Saúde', ARRAY['alongamento'], FALSE, '2026-04-13 07:00:00-03', NULL),
  ('Revisar código', 'Code review', ARRAY['PR1','PR2','feedback'], TRUE, '2026-04-14 16:00:00-03', '2026-04-14 17:30:00-03');