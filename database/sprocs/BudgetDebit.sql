create or replace procedure BudgetDebit(
   budget_id int,
   amount numeric
)
language plpgsql    
as $$
DECLARE 
    selected_budget RECORD;
begin
    if amount < 0 then
        raise exception 'BudgetInvalidAmountException : Amount % is Negative for ID %', amount, budget_id;
    end if;
    select into selected_budget * from budget where id = budget_id;

    if not found then
        raise exception 'BudgetNoRecordException : No Budget Found for ID %', budget_id; 
    end if;
    update budget
    set available = selected_budget.available + amount,
    updated_at = CURRENT_TIMESTAMP
    where id = selected_budget.id;

end$$;