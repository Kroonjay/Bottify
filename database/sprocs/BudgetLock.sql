create or replace procedure BudgetLock(
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
    -- subtracting the amount from the sender's account 
    if (selected_budget.available - amount) < 0 then
        raise exception 'BudgetInsufficientFundsException : Debit Amount % Larger than Available value for Budget ID %', amount, selected_budget.id;
    end if;
    update budget 
    set available = selected_budget.available - amount,
    reserved = selected_budget.reserved + amount,
    updated_at = CURRENT_TIMESTAMP
    where id = budget_id;

end$$;