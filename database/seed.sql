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