import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = ValidateTypeValidator.class)
@Target({ ElementType.FIELD })
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidateType {

    String message() default "Invalid value";

    String[] list(); // Allowed values

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
