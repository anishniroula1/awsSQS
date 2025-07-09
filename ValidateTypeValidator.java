import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

public class ValidateTypeValidator implements ConstraintValidator<ValidateType, Object> {

    private Set<String> allowedValues;

    @Override
    public void initialize(ValidateType constraintAnnotation) {
        allowedValues = new HashSet<>(Arrays.asList(constraintAnnotation.list()));
    }

    @Override
    public boolean isValid(Object value, ConstraintValidatorContext context) {
        if (value == null) return true;

        if (value instanceof String) {
            return allowedValues.contains(value);
        }

        if (value instanceof Collection<?>) {
            for (Object item : (Collection<?>) value) {
                if (!(item instanceof String) || !allowedValues.contains(item)) {
                    return false;
                }
            }
            return true;
        }

        if (value.getClass().isArray()) {
            Object[] array = (Object[]) value;
            for (Object item : array) {
                if (!(item instanceof String) || !allowedValues.contains(item)) {
                    return false;
                }
            }
            return true;
        }

        return false;
    }
}
