create or replace procedure BudgetCredit(
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
    elsif (selected_budget.reserved - amount) < 0 then
        raise exception 'BudgetInsufficientFundsException : Credit Amount % Larger than Reserve value for Budget ID %', amount, budget_id;
    else
        update budget 
        set reserved = selected_budget.reserved - amount,
        updated_at = CURRENT_TIMESTAMP
        where id = selected_budget.id;
    end if;

end$$;